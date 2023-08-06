from Products.CacheSetup import config
from Products.CacheSetup.Extensions import policy_1, policy_2

POLICIES = (policy_1, policy_2)

def updateOldCachePolicy(portal, out):
    ct = getattr(portal, config.CACHE_TOOL_ID)
    rules = getattr(ct, config.RULES_ID, None)
    if rules is not None and rules.portal_type == 'RuleFolder':
        # this is an old policy so make it a new-style policy folder
        oldpolicy_id = "old-policy"
        oldpolicy_title = "Old Cache Policy - saved from previous install"
        ct.addPolicyFolder(oldpolicy_id, oldpolicy_title)
        oldpolicy = getattr(ct, oldpolicy_id)
        folder_ids = [config.RULES_ID, config.HEADERSETS_ID]
        cp = ct.manage_copyObjects(folder_ids)
        oldpolicy.manage_pasteObjects(cp)
        for folder in oldpolicy.objectValues():
            folder.unmarkCreationFlag()
            for item in folder.objectValues():
                item.unmarkCreationFlag()
        ct.setActivePolicyId(oldpolicy_id)
        ct.manage_delObjects(folder_ids)
        # let's also migrate cacheConfig
        cache_config = ct.getCacheConfig()
        if cache_config in ('zserver','apache'):
            ct.setProxyPurgeConfig('no-purge')
        elif cache_config == 'squid':
            ct.setProxyPurgeConfig('no-rewrite')
        else:
            ct.setProxyPurgeConfig('custom-rewrite')
    else:
        # this is cachefu version 1.1+
        # let's retitle old policies to avoid confusion
        suffix_save = "saved from previous install"
        suffix_copy = "copy"
        policies = [p for p in ct.objectValues() if p.portal_type=="CachePolicy"]
        for policy in policies:
            policy_title = policy.Title()
            suffix = suffix_save in policy_title and suffix_copy or suffix_save
            policy.setTitle('%s - %s' % (policy_title, suffix))

def addCachePolicies(portal, out):
    # We'll extend this later
    # preferably using GenericSetup profiles
    ct = getattr(portal, config.CACHE_TOOL_ID)
    for p in POLICIES:
        # fix any id collisions
        if getattr(ct, p.POLICY_ID, None) is not None:
            count = 1
            while getattr(ct, '%s-backup%s' % (p.POLICY_ID, count), None) is not None:
                count = count + 1
            newId = '%s-backup%s' % (p.POLICY_ID, count)
            ct.manage_renameObjects([p.POLICY_ID], [newId])
        # now add the new policy
        ct.addPolicyFolder(p.POLICY_ID, p.POLICY_TITLE)
        rules = ct.getRules(p.POLICY_ID)
        p.addCacheRules(rules)
        header_sets = ct.getHeaderSets(p.POLICY_ID)
        p.addHeaderSets(header_sets)
    # Lets move the new policies to the top of the list
    policy_ids = [p.POLICY_ID for p in POLICIES]
    ct.moveObjectsToTop(policy_ids)


