##

"""
The ConfigLoader loads in a particular configuration file that
specifies the change definition to be run.
"""
import re
import sys
import os

from lxml import etree

from namespace import create_namespace
from iterator import create_iterator
from device import Device
from change import CHANGE_STATE, ChangeConditionFailure, NoCommands
from provisioner import UserBailout
import util

from twisted.internet import defer, reactor
from twisted.python import log as tlog

import logging
import debug

log = logging.getLogger('modipy')

xinclude_re = re.compile(r'.*<xi:include href=[\'\"](?P<uri>.*)[\'\"].*')

class ConfigLoader:
    """
    A ConfigLoader is used to load in a change configuration and
    set up all the objects that define the change.
    """

    def __init__(self):

        self.doc = None

        self.global_namespace = {}

        self.provisioners = {}
        self.devices = {}
        self.change_templates = {}
        self.changes = {}
        self.iterators = {}

        self.pending_changes = []
        self.change_success = []
        self.change_failure = []
        self.backout_success = []
        self.backout_failure = []

        log.debug("created ConfigLoader")

    def load_config(self, options, devices=[]):

        self.options = options

        d = defer.succeed(None)

        if options.configfile:
            d.addCallback(self.parse, options.configfile)
            pass

        # Add devices specified on the commandline to the active configuration
        if len(devices) != 0:
            for dev in devices:
                # If a device given on the commandline is not present in the
                # configuration file, add it.
                if dev not in self.devices.keys():
                    log.info("Adding commandline specified device: '%s'" % dev)
                    self.devices[dev] = Device(dev)
                    pass
                pass
                # If devices other than those specified on the commandline
                # ARE present in the config file, remove the extra ones.
                # This means you can run a configuration on a subset of devices
                # by specifying the device name on the commandline.

            for dev in self.devices.keys():
                if dev not in devices:
                    log.info("Not using configured device '%s' (not on commandline)", dev)
                    del self.devices[dev]
                    pass
                pass
            pass

        return d
            
    def parse(self, ignored, configfile):
        """
        Parse my configuration file.
        """
        try:
            self.tree = etree.parse(configfile)
        except IOError, e:
            log.error("Cannot parse configuration file: %s", e)
            raise

        # Process xincludes
        try:
            self.tree.xinclude()
        except etree.XIncludeError:
            log.error("XInclude of a file failed.")
            log.error("Use external tool such as xmllint to figure out why.")
            log.error("Sorry, but lxml.etree won't tell me exactly what went wrong.")
            raise
            
        # add the global namespace
        try:
            nsnode = self.tree.xpath('/config/namespace')[0]
            self.add_namespace(None, nsnode)
        except IndexError:
            # use default global_namespace defined in __init__
            pass

        d = defer.succeed(None)

        # Add all my node types, in the order specified in the list
        for nodename in [
            'iterator',
            'provisioner',
            'device',
            'changetemplate',
            'change',
#            'dependencies',
            ]:

            for node in self.tree.findall(nodename):
                # Find the function to call based on the name of
                # the object by using dynamic lookup
                # This will call 'add_iterator' for an iterator node, for example.
                funcname = 'add_%s' % nodename
                func = getattr(self, funcname)
                d.addCallback(func, node)
                pass
            pass
        
        d.addCallback(self.set_prereqs)
        return d

    def set_prereqs(self, ignored):

        # Find all the prereq definitions
        prereqs = self.tree.findall('prereq')
        for node in prereqs:
            prereq_changename = node.text

            try:
                prereq_for = node.attrib['for']
            except KeyError:
                # See if this prereq node is within a change node
                prereq_for = node.xpath("parent::*/change")[0].attrib['name']
                log.debug("Using change name of '%s'", prereq_for)
                
            # find the change
            try:
                prereq_change = self.changes[prereq_changename]
            except KeyError:
                log.error("Cannot find change '%s' as prereq for change '%s'", prereq_changename, prereq_for)
                raise

            try:
                change_for = self.changes[prereq_for]
            except KeyError:
                log.error("Cannot find change '%s' with prereq of '%s'", prereq_for, prereq_changename)
                raise

            # add change as prereq
            change_for.pre_requisites.append(prereq_change)
            log.debug("Added change '%s' as prereq for change '%s'", prereq_changename, prereq_for)

        # once the parse has completed, do some post-parse setup
        self.process_dependencies()

    def add_iterator(self, ignored, node):
        """
        Add an iterator, which is a list of namespaces
        that will be iterated over for a particular change step.
        """
        iter = create_iterator(node)
        self.iterators[iter.name] = iter
        log.debug("Added iterator '%s'", iter.name)
        return iter.load_config(None)

    def import_module(self, module_name):
        """
        Custom dynamic import function to import change and provisioner modules.
        """
        try:
            mod = sys.modules[module_name]
            return mod
        except KeyError:
            log.debug("module '%s' not yet imported. Importing...", module_name)
            mod = __import__(module_name)
            components = module_name.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
                pass
            return mod
        
    def add_provisioner(self, ignored, node):
        """
        Add a provisioner to my configuration based on the parsed element.
        """
        # Provisioner type is dynamic, as it supports the loading
        # of plugin modules at runtime, so we look up the type
        prov_klass = node.attrib['type']
        prov_name = node.attrib['name']
        try:
            module_name = node.attrib['module']
        except KeyError:
            module_name = 'modipy.provisioner'
            
        # Copy the attribs into a dictionary for use as kwargs
        kwargs = {}
        for key in node.attrib:
            if key not in ['type', 'name', 'module']:
                kwargs[key] = node.attrib[key]

        log.debug("Attempting to create a '%s' provisioner", prov_klass)
        prov_module = self.import_module(module_name)
        log.debug("prov_module is: %s", prov_module)
        klass = getattr( prov_module, prov_klass )
        try:
            provisioner = klass(prov_name, authoritarian=self.options.authoritarian,
                                autobackout=self.options.autobackout,
                                **kwargs)
        except TypeError, e:
            log.error("Incorrect parameter supplied for provisioner of type '%s'", prov_klass)
            raise e

        log.debug("created provisioner '%s': %s", prov_name, provisioner)

        # If there are further attributes for the provisioner,
        # handle them with the provisioner itself
        for subnode in node.xpath('*'):
            provisioner.parse_config_node(subnode)
            pass

        self.provisioners[prov_name] = provisioner

    def add_device(self, ignored, node):
        """
        Add a device to my configuration based on the parsed element.
        """
        device_name = node.attrib['name']
        device = Device(device_name)

        # add an attribute for each sub-element
        for subnode in node.xpath('*'):
            attrib = subnode.tag
            value = subnode.text
            setattr(device, attrib, value)
            pass

        log.debug("created device: %s", device)
        self.devices[device_name] = device

    def add_changetemplate(self, ignored, node):
        """
        Add a change template to my list of available templates.
        A change template is a change object that may not have
        all of its parameters set yet.
        """
        # Create the change template object
        change_tmpl = self.create_change_object(node)
        
        # Set change parameters that are common to all changes
        self.set_change_params(change_tmpl, node)

        # Set any namespaces
        self.set_change_namespace(change_tmpl, node)

        # Set the optional change provisioner
        self.set_change_provisioner(change_tmpl, node)
        
        # Set the optional change iterator
        self.set_change_iterator(change_tmpl, node)
        
        # Add an optional onfail mode
        self.set_change_onfail(change_tmpl, node)

        self.change_templates[change_tmpl.name] = change_tmpl

        return change_tmpl

    def add_change(self, ignored, node):
        """
        When adding a change, check for some extra options such as a
        change template, which will cause this change to be based on
        an existing change template.
        """
        log.debug("Adding new change...")
        if node.attrib.has_key('template'):
            tmpl_name = node.attrib['template']
            log.debug("Change is based on a template: '%s'", tmpl_name)
            # Do template based processing
            try:
                template = self.change_templates[tmpl_name]
            except KeyError:
                raise ValueError("Change template '%s' is not defined" % tmpl_name)

            change = template.copy()
            # Make sure we set the change name to the actual change,
            # not the name of the template
            change.name = node.attrib['name']

            # Now do non-templated specific processing
            self.set_change_params(change, node)
            self.set_change_namespace(change, node)
            self.set_change_provisioner(change, node)
            self.set_change_iterator(change, node)
            self.set_change_onfail(change, node)
            
        else:
            # Use the same processing stream as a template, with the
            # assumption that all the required parameters have been
            # defined. If they haven't, the change will fail.
            change = self.add_changetemplate(None, node)
            pass
        
        # If the change doesn't have a provisioner, use the first one
        # in our config by default.
        if getattr(change, 'provisioner', None) is None:
            for prov in self.provisioners.values():
                log.debug("Checking provisioner: '%s'", prov)
                if change.provisioner_interface.providedBy(prov):
                    log.debug("change '%s' will use provisioner '%s'", change.name, prov.name)
                    change.provisioner = prov
                    break
                else:
                    log.debug("provisioner '%s' does not provide interface %s", prov.name, change.provisioner_interface)
                    pass
                pass
            pass
        # If, after all that, we can't find a provisioner for the change, bail.
        if change.provisioner is None:
            raise ValueError("No compatible provisioners exist for change '%s'" % change.name)
        
        self.changes[change.name] = change
        self.pending_changes.append( change )

    def create_change_object(self, node):
        """
        Create a change object from a node.
        This may be used as a change template, or a regular change.
        """
        # Change type is dynamic, as it supports the loading
        # of plugin modules at runtime, so we look up the type
        try:
            change_name = node.attrib['name']
            log.debug("Creating change object '%s'...", change_name)
        except KeyError:
            log.error("Change definition has no name")
            raise

        try:
            change_klass = node.attrib['type']
        except KeyError:
            log.error("Change definition for '%s' has no type.", change_name)
            raise

        try:
            module_name = node.attrib['module']
        except KeyError:
            module_name = 'modipy.change_command'
        
        log.debug("Creating a '%s' change", change_klass)
        change_module = self.import_module(module_name)
        log.debug("Loaded change module: %s", change_module)
        klass = getattr(change_module, change_klass)

        change = klass(change_name, nopause=self.options.nopause)

        log.debug("created change '%s': %s", change_name, change)
        return change

    def set_change_namespace(self, change, node):
        """
        Add a namespace to a change or change template
        """
        log.debug("change namespace: %s", change.namespace)
        if change.namespace == {}:
            # FIXME: using global namespace as change namespace may be wrong.
            log.debug("change has no namespace, using the global one.")
            change.namespace = self.global_namespace

    def set_change_provisioner(self, change, node):
        # which provisioner to use for the change
        try:
            provname = node.attrib['provisioner']
        except KeyError:
            return
        
        provname = util.substituteVariables(provname, change.namespace)
        try:
            prov = self.provisioners[provname]
        except KeyError:
            raise KeyError("Provisioner named '%s' is not defined" % provname)

        if not change.provisioner_interface.providedBy(prov):
            raise ValueError("Provisioner '%s' does not provide interface '%s' required by change '%s'" % (prov.name, change.provisioner_interface, change.name))

        change.provisioner = prov

    def set_change_params(self, change, node):
        """
        Set common change parameters, defined in subnodes.
        """
        for subnode in node.xpath('*'):
            # a target device for the change
            if subnode.tag == 'target':
                targetname = subnode.attrib['name']

                log.debug("-- Found targetname: %s", targetname)

                # Parse special targetname ALL_TARGETS
                if targetname == 'ALL_TARGETS':
                    change.devices.extend( self.devices.values() )
                    devicenames = ','.join( [ '%s' % x for x in self.devices.keys() ] )
                    log.debug("added target devices '%s' for change '%s'", devicenames, change)
                else:
                    # perform variable substitution with global namespace
                    targetname = util.substituteVariables(targetname, change.namespace)
                    try:
                        dev = self.devices[targetname]
                    except KeyError, e:
                        raise KeyError("Device '%s' not defined" % targetname)
                    change.devices.append(dev)
                    log.debug("added target device '%s' for change '%s'", dev, change)
                pass

            elif subnode.tag == 'depends':
                changename = subnode.attrib['on']
                try:
                    change.pre_requisites.append(self.changes[changename])
                except KeyError:
                    if changename == change.name:
                        log.error("Change '%s' cannot be a pre-requisite of itself.", changename)
                        pass
                    else:
                        log.error("Configuration error: Unknown pre-requisite '%s' for change '%s'", changename, change.name)
                        pass
                    raise
                log.debug("added change pre-requisite: '%s' for change '%s'", changename, change)

            #
            # The following attributes need to be parsed by the change
            # implementation itself, as the permitted contents of the
            # node varies depending on the change type. For example,
            # the implementation actions for a CommandChange are unix-style
            # commandline invokations, while a ZAPIChange might specify
            # NetApp ZAPI documents
            #
            else:
                method_name = 'parse_%s' % str(subnode.tag)
                method = getattr(change, method_name)
                method(subnode)
                pass
            pass
        pass

    def set_change_iterator(self, change, node):
        """
        Set an optional change iterator
        """
        try:
            itername = node.attrib['iterator']
        except KeyError:
            itername = None

        if itername is not None:
            # Use namespace substitution for the itername to allow templating
            itername = util.substituteVariables(itername, change.namespace)
            try:
                change.iterator = self.iterators[itername]
                log.debug("change '%s' will iterate with iterator '%s'" % (change.name, itername))
            except KeyError:
                log.error("Iterator '%s' is not defined", itername)
                raise
            pass
        pass

    def set_change_onfail(self, change, node):
        """
        Attempt to add an 'onfail' mode for the change, if defined
        """
        log.debug("Checking for 'onfail' attribute...")
        try:
            onfail = node.attrib['onfail']
            log.debug("onfail attrib found.")
            if onfail == 'continue':
                change.on_fail_continue = True
                log.debug("Processing will continue if this change fails")

            elif onfail == 'retry':
                change.on_fail_retry = True
                log.debug("This change will retry on failure")
                try:
                    max_retries = int(node.attrib['max_retries'])
                    change.max_retries = max_retries
                except KeyError:
                    pass
                log.debug("  This change will retry at most %d times", change.max_retries)

                try:
                    retry_delay = int(node.attrib['retry_delay'])
                    if retry_delay < 0:
                        raise ValueError("Retry delay for change '%s' must be > 0" % change.name)
                    
                    change.retry_delay = retry_delay
                except KeyError:
                    pass

        except KeyError:
            pass

    def set_change_noop(self, change, node):
        """
        Mark a change as a 'No Op' if it has the noop attribute set.
        If it's not set to anything, this is taken as meaning 'true'.
        If it's absent, then it
        """
        try:
            onfail = node.attrib['noop']
            log.debug("noop attrib found")
            if not ( noop.lower().startswith('n') or noop.lower().startswith('f') ):
                change.noop = True
        except KeyError:
            pass

    def add_namespace(self, ignored, node, item=None):
        """
        Add a namespace, defined by nsnode, to an item (such as a change)
        This is called within an 'add_' method for the other items,
        such as iterators and changes.
        """
        log.debug("Adding namespace: node")
        
        ns = create_namespace(node)

        if item is None:
            # This is the global namespace
            self.global_namespace = ns
        else:
            log.debug("Adding namespace to item: %s", item)
            ns.parent = self.global_namespace
            item.namespace = ns

    def get_available_changes(self):
        """
        This returns a list of pending changes that can be performed,
        either because they have no pre-requsites, or all their
        pre-requisistes have been successfully implemented.
        """
        changelist = []
        log.debug("pending changes: %s", self.pending_changes)
        for change in self.pending_changes:
            log.debug("testing change %s", change)
            if len(change.pre_requisites) == 0:
                changelist.append(change)
                log.debug("change '%s' has no pre-reqs. Adding to execution queue.", change)
                continue

            else:
                all_prereqs = True
                for prereq in change.pre_requisites:
                    log.debug("change '%s' has a pre-req of '%s'", change, prereq)
                    if prereq not in self.change_success:

                        # If we're in backout mode, a prereq in 'backout_ok' state
                        # is treated as complete.
                        if prereq.state in [ CHANGE_STATE['backout_ok'], ]:
                            continue

                        # If a prereq has failed, doesn't need to retry, and is
                        # marked as 'onfail:continue', then we treat it as if
                        # this prereq has been met.
                        elif prereq.state not in [ CHANGE_STATE['pending'],
                                                 CHANGE_STATE['retry'],
                                                 ] and prereq.on_fail_continue:
                            log.debug("prereq failed, but is marked onfail:continue.")
                            continue

                        log.debug("pre-req '%s' not complete yet.", prereq)
                        all_prereqs = False
                        break
                    pass

                if all_prereqs:
                    log.debug("All pre-reqs for '%s' have completed. Adding to execution queue.", change)
                    changelist.append(change)
                else:
                    log.debug("change '%s' has pending pre-reqs", change)

        log.debug("Returning changelist: %s", changelist)
        return changelist

    def change_complete(self, fail_result, change):
        """
        Move a change from pending to complete.
        """
        if change.state == CHANGE_STATE['success']:
            self.change_success.append(change)
            self.pending_changes.remove(change)

        elif change.state == CHANGE_STATE['partial_failure']:
            self.change_failure.append(change)
            self.pending_changes.remove(change)

        elif change.state == CHANGE_STATE['total_failure']:
            self.change_failure.append(change)
            self.pending_changes.remove(change)

        elif change.state == CHANGE_STATE['backout_ok']:
            self.change_failure.append(change)
            self.backout_success.append(change)
            self.pending_changes.remove(change)

        elif change.state == CHANGE_STATE['backout_failed']:
            self.change_failure.append(change)
            self.backout_failure.append(change)
            self.pending_changes.remove(change)

        elif change.state == CHANGE_STATE['retry_pending']:
            log.info("Change '%s' will be retried in '%d' seconds", change.name, change.retry_delay)
            pass

        elif change.state == CHANGE_STATE['retry']:
            log.info("Change '%s' will be retried", change.name)
            pass

        elif change.state == CHANGE_STATE['pending']:
            log.error("Change '%s' did not run.", change.name)
            self.pending_changes.remove(change)
            pass
        
        else:
            log.error("Unknown/unhandled change state '%s'", change.state)
            self.pending_changes.remove(change)
            raise ValueError("change_complete() cannot handle change state: %s", change.state)

    def _apply_namespace(self, string, namespace):
        """
        Apply a namespace to a string
        Deprecated
        """
        if namespace is not None:
            string = string % namespace

        return string

    def process_dependencies(self):
        """
        Post-process the dependency tree after loading it.
        This sets up the pre-reqs for each change, as specified
        in the dependency tree.
        """
        # Fetch the list of changes with dependencies
        for node in self.tree.findall('dependencies'):
            log.debug("dependency node: %s", node)

class ChangeController:
    """
    An overall change controller, to control the changes
    """

    def __init__(self, config_loader):

        self.cfgldr = config_loader

        self.current_changelist = []

        # a Deferred that gets set up when do_changes() is called
        self.alldone = None 

    def do_changes(self, ignored):
        self.alldone = defer.Deferred()

        self.get_next_changes(None)

        # print statistics for what happened, no matter if it's callback or errback
        self.alldone.addCallbacks(self.print_stats, self.print_stats)

        # deal with errors in stats
        #self.alldone.addErrback(self.print_stats)
                                
        return self.alldone

    def get_next_changes(self, results):

        """
        Fetch the next set of changes to run.
        This collects all changes that don't have any
        pre-requisites (on the first pass), or that have had all
        their pre-requisites complete successfully.
        These changes can therefore all be run together, since they
        have no interdependencies on one another.
        """
        log.debug("Results in get_next_changes are: %s", results)
        log.debug("Fetching outstanding changes...")
        self.current_changelist = self.cfgldr.get_available_changes()

        if len(self.current_changelist) == 0:
            if len(self.cfgldr.pending_changes) > 0:
                log.error("Pending changes exist that cannot be executed!")
                self.alldone.errback(ValueError("Pending changes cannot be executed"))
            else:
                # No more changes, all changes completed.
                if self.alldone is not None:
                    self.alldone.callback("All changes complete")
                    #self.alldone = None
            pass
        else:
            # If there are pending changes, add that call to the deferred
            log.debug("Pending changes to be executed. Scheduling.")
            return self.do_pending_changes(None)

    def do_pending_changes(self, ignored):
        """
        This runs all the pending changes that are currently queued.
        It runs all of them simultaneously, since they have been identified
        as changes that can be run together. If you want to run changes
        sequentially, then they should have sequential dependencies.

        FIXME: Maybe add a flag to allow sequential mode operation?
        """
        log.debug("Running pending changes...")
        dlist = []

        log.debug("changelist is: %s", self.current_changelist)
        for change in self.current_changelist:

            log.debug("adding change '%s' to implementation queue", change.name)
                
            d = change.provisioner.perform_change(None, change, self.cfgldr.global_namespace, backout=self.cfgldr.options.backout)
            d.addCallback(self.change_complete, change)
            d.addErrback(self.change_failure, change)
            dlist.append(d)
            pass

        dl = defer.DeferredList(dlist, fireOnOneErrback=True, consumeErrors=True )
        #dl = defer.gatherResults(dlist)
        #dl = defer.DeferredList(dlist, fireOnOneErrback=True, consumeErrors=True)
        # After the current crop of changes has been completed, find if there are more
        dl.addCallback( self.get_next_changes )
        dl.addErrback( self.bailout )
        return dl

    def bailout(self, failure):
        """
        Bailout detects the first error from the deferred list,
        and bails out.
        """
        log.debug("Running bailout because of: %s", failure)
        #tlog.err(failure)
        if failure.value.subFailure.type == UserBailout:
            self.alldone.callback('Bailout')
        else:
            log.debug("Unhandled bailout failure: %s", failure)
            self.alldone.errback(failure.value.subFailure)

    def change_complete(self, result, change):
        """
        Move change from pending to complete
        """
        self.cfgldr.change_complete(result, change)

    def change_failure(self, failure, change):
        if failure.type == UserBailout:
            log.debug("Controller detected UserBailout")
            self.change_complete(failure, change)
            return failure

        elif failure.type == ChangeConditionFailure:
            log.debug("Controller detected ChangeConditionFailure")
            self.change_complete(failure, change)
            pass

        elif failure.type == NoCommands:
            #log.error(failure.value)
            self.change_complete(failure, change)
            return failure

        else:
            log.error("Major change failure: %s", failure.value)
            #tlog.err(failure)
            self.change_complete(failure, change)
            return failure

    def print_stats(self, ignored):
        """
        We've finished all our work, and now we summarise what happened.
        """
        success_count = len(self.cfgldr.change_success)
        failure_count = len(self.cfgldr.change_failure)
        backout_success_count = len(self.cfgldr.backout_success)
        backout_failure_count = len(self.cfgldr.backout_failure)
        pending_count = len(self.cfgldr.pending_changes)

        log.info("--- Final results ---")

        # Don't print some stats when in backout mode
        if not self.cfgldr.options.backout:
        
            if not (success_count > 0 or failure_count > 0):
                log.error("no changes succeeded or failed!")
            else:
                log.info("%d ok, %d failed (%d%% success rate)" % (success_count, failure_count, 100 * success_count / (success_count+failure_count) ) )

            if success_count > 0:
                log.info( "Successful changes: %s" % ', '.join([ x.name for x in self.cfgldr.change_success]))

            if failure_count > 0:
                log.info( "Failed changes: %s" % ', '.join([ x.name for x in self.cfgldr.change_failure]) )
                pass
            pass

        # These stats are always printed

        if backout_success_count > 0 or backout_failure_count > 0:
            log.info( "%d backed out ok, %d failed (%d%% backout success rate)" % (backout_success_count, backout_failure_count, 100 * backout_success_count / (backout_success_count+backout_failure_count) ))
            
        if backout_success_count > 0:
            log.info( "Changes backed out ok: %s" % ', '.join([ x.name for x in self.cfgldr.backout_success]))

        if backout_failure_count > 0:
            log.error( "Changes NOT backed out ok: %s" % ', '.join([ x.name for x in self.cfgldr.backout_failure]))

        if pending_count > 0:
            if pending_count > 1:
                plural = 's'
                waswere = 'were'
            else:
                plural = ''
                waswere = 'was'
                pass

            log.info( "%d change%s %s not attempted: %s" % (pending_count, plural, waswere, ', '.join([ x.name for x in self.cfgldr.pending_changes ]) ) )


if __name__ == '__main__':

    #log.setLevel(logging.DEBUG)
    log.setLevel(logging.INFO)

    configfile = 'etc/test_change.conf'

    try:
        cfgldr = ConfigLoader(configfile)
    except:
        log.error("Cannot load configuration. Aborting.")
        sys.exit(1)

    log.debug("changes to apply: %s", cfgldr.changes)
    log.debug("total devices: %s", cfgldr.devices)

    controller = ChangeController(cfgldr)

    def mystop(ignored):
        log.debug("finished!")
        reactor.stop()
        pass

    def errstop(failure):
        log.error("Changes not implemented ok!")
        #tlog.err(failure)
        reactor.stop()
        
    def go():
        d = controller.do_changes()        
        d.addCallbacks(mystop, errstop)
        
    # Use callLater(0) syntax to trigger running of changes once
    # the reactor has actually started, so it can be stopped cleanly.
    reactor.callLater(0, go)
    reactor.run()
        
