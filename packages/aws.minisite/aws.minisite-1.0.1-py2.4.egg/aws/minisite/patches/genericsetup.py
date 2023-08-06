# -*- coding: utf-8 -*-
## Copyright (C) 2010 Ingeniweb - all rights reserved
## No publication or distribution without authorization.
import logging
from zope import event
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup import tool, metadata, utils, events

LOG = logging.getLogger(__name__)

def aws_minisite_getImportMapping( self ):

    return {
        'metadata':
        {'description': { utils.CONVERTER: self._convertToUnique },
         'version': { utils.CONVERTER: self._convertToUnique },
         'dependencies': { utils.CONVERTER: self._convertToUnique },
         'products': {utils.CONVERTER: self._convertToUnique},
         },
        'description':
        { '#text': { utils.KEY: None, utils.DEFAULT: '' },
          },
        'version':
        { '#text': { utils.KEY: None },
          },
        'dependencies':
        {'dependency': { utils.KEY: None },},
        'dependency':
        { '#text': { utils.KEY: None },
          },
        'products':
        {'product': {utils.KEY: None},},
        'product':
        {'#text': {utils.KEY: None},}
        }

metadata.ProfileMetadata._getImportMapping = aws_minisite_getImportMapping
LOG.info('PATCHED GenericSetup.metadata.ProfileMetadata._getImportMapping to '
         'support products dependencies')

def aws_minisite_runImportStepFromProfile(self, profile_id, step_id,
                                       run_dependencies=True, purge_old=None):
    """ See ISetupTool.
    """
    old_context = self._import_context_id
    context = self._getImportContext(profile_id, purge_old)

    self.applyContext(context)

    info = self.getImportStepMetadata(step_id)

    if info is None:
        self._import_context_id = old_context
        raise ValueError, 'No such import step: %s' % step_id

    dependencies = info.get('dependencies', ())

    messages = {}
    steps = []

    if run_dependencies:
        qi = getToolByName(self, 'portal_quickinstaller').aq_inner
        products = info.get('products', ())
        for product in products:
            if not qi.isProductInstalled(product):
                qi.installProduct(product)

        for dependency in dependencies:
            if dependency not in steps:
                steps.append(dependency)
    steps.append (step_id)

    full_import=(set(steps)==set(self.getSortedImportSteps()))
    event.notify(events.BeforeProfileImportEvent(self, profile_id, steps, full_import))

    for step in steps:
        message = self._doRunImportStep(step, context)
        messages[step] = message or ''

    message_list = filter(None, [message])
    message_list.extend( ['%s: %s' % x[1:] for x in context.listNotes()] )
    messages[step_id] = '\n'.join(message_list)

    self._import_context_id = old_context

    event.notify(events.ProfileImportedEvent(self, profile_id, steps, full_import))

    return { 'steps' : steps, 'messages' : messages }

tool.SetupTool.runImportStepFromProfile = aws_minisite_runImportStepFromProfile

def aws_minisite_getProductsForProfile(self, profile_id):
    if profile_id.startswith("snapshot-"):
        return ()

    if not self.profileExists( profile_id ):
        raise KeyError, profile_id
    try:
        return self.getProfileInfo( profile_id ).get('products', ())
    except KeyError:
        return ()

tool.SetupTool.getProductsForProfile = aws_minisite_getProductsForProfile

def aws_minisite_getProductDependencyChain(self, profiles):
    profiles = set(profiles)
    return [str(product)
            for profile in profiles
            for product in self.getProductsForProfile(profile)]

tool.SetupTool.getProductDependencyChain = aws_minisite_getProductDependencyChain

def aws_minisite_runImportStepsFromContext(self,
                                        steps=None,
                                        purge_old=None,
                                        profile_id=None,
                                        archive=None,
                                        ignore_dependencies=False,
                                        seen=None):

    if profile_id is not None and not ignore_dependencies:
        try:
            chain = self.getProfileDependencyChain( profile_id )
            products = self.getProductDependencyChain(chain)
        except KeyError, e:
            logger = logging.getLogger('GenericSetup')
            logger.error('Unknown step in dependency chain: %s' % str(e))
            raise
    else:
        products = []
        chain = [ profile_id ]
        if seen is None:
            seen=set()
        seen.add( profile_id )

    results = []

    try:
        qi = getToolByName(self, 'portal_quickinstaller')
    except AttributeError:
        # at construction time portal has only 'portal_setup'
        qi = None

    if qi is not None:
        qi = qi.aq_inner
        for product in products:
            if not qi.isProductInstalled(product):
                qi.installProduct(product)

    detect_steps = steps is None

    for profile_id in chain:
        context = self._getImportContext(profile_id, purge_old, archive)
        self.applyContext(context)

        if detect_steps:
             # this will extends import steps so that 'final' steps of this
             # dependency profile gets included        
            steps = self.getSortedImportSteps()
        messages = {}

        event.notify(events.BeforeProfileImportEvent(self, profile_id, steps, True))
        for step in steps:
            message = self._doRunImportStep(step, context)
            message_list = filter(None, [message])
            message_list.extend( ['%s: %s' % x[1:]
                                  for x in context.listNotes()] )
            messages[step] = '\n'.join(message_list)
            context.clearNotes()

        event.notify(events.ProfileImportedEvent(self, profile_id, steps, True))

        results.append({'steps' : steps, 'messages' : messages })

    data = { 'steps' : [], 'messages' : {}}
    for result in results:
        for step in result['steps']:
            if step not in data['steps']:
                data['steps'].append(step)

        for (step, msg) in result['messages'].items():
            if step in data['messages']:
                data['messages'][step]+="\n"+msg
            else:
                data['messages'][step]=msg
    data['steps'] = list(data['steps'])

    return data

tool.SetupTool._runImportStepsFromContext = aws_minisite_runImportStepsFromContext

LOG.info('PATCHED tool.SetupTool to install product dependencies')
