# Copyright 2008 Lime Nest LLC
# Copyright 2008 Lime Spot LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import binascii

repository = None
from mercurial import context, hg, node, repo, ui

try:
    repository = hg.repository(ui.ui(), '.')
except repo.RepoError:
    pass
else:

    current_ctx = context.changectx(repository)

    def info(ctx = current_ctx):
        return {
                 'rev': ctx.rev(),
                 'node': ctx.node(),
                 'branch': ctx.branch(),
                 'tags': ctx.tags()
               }

    def close_non_tip_tag(ctx):
        ntt = non_tip_tag(ctx.tags())
        if ntt is not None: return ntt
    
        for parent in ctx.parents():
            ntt = non_tip_tag(parent.tags())
            if ntt is None: continue
    
            tagging_description = "Added tag %s for changeset %s" % (ntt, node.short(parent.node()))
            if ctx.description() == tagging_description: return ntt
    
        return None

    def non_tip_tag(tags):
        for tag in tags:
            if tag != 'tip': return tag
    
        return None
    
    def most_recent_non_tip_tag(ctx):
    #    print "ctx: %s" % ctx.rev()
        ntt = non_tip_tag(ctx.tags())
        if ntt is not None: return ntt
    
        if ctx.rev() >= 0:
            for parent in ctx.parents():
                ntt = most_recent_non_tip_tag(parent)
                if ntt is not None: return ntt
    
        return None
    
    
    def version():
        ntt = close_non_tip_tag(current_ctx)
        if ntt is not None: return ntt
    
        base_version = most_recent_non_tip_tag(current_ctx)
        if base_version is None: base_version = "0.0"
    
        i = info()
        return '%s-r%s_%s' % (base_version,i['rev'], binascii.hexlify(i['node']))
        
        
        
        
        
        
