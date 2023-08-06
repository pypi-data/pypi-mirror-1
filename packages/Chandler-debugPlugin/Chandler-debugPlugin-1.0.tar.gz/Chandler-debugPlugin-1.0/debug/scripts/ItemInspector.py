#   Copyright (c) 2003-2006 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


# prints the item that's currently selected.

import osaf.framework.blocks.Block as Block

f = Block.Block.getFocusBlock()
i = getattr(f, "selectedItemToView", None)
if i is None:
    try:
        i = f.selection[0]
    except (IndexError, AttributeError):
        i = None
if i is not None:
  print i.displayName.encode('utf8'), repr(i)
else:
  print None
