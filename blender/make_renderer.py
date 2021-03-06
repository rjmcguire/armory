import bpy
import nodes_renderpath

group = None
nodes = None
links = None

def make_renderer(cam):
    global group
    global nodes
    global links

    if cam.rp_renderer == 'Forward':
        nodes_renderpath.load_library('forward_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_forward(cam)
    else: # Deferred
        nodes_renderpath.load_library('deferred_path', 'armory_default')
        group = bpy.data.node_groups['armory_default']
        nodes = group.nodes
        links = group.links
        make_deferred(cam)

def relink(start_node, next_node):
    n = nodes[start_node].inputs[0].links[0].from_node
    l = n.outputs[0].links[0]
    links.remove(l)
    links.new(n.outputs[0], nodes[next_node].inputs[0])

def make_forward(cam):

    nodes['Begin'].inputs[1].default_value = cam.rp_hdr
    nodes['Screen'].inputs[0].default_value = int(cam.rp_supersampling)

    if cam.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(cam.rp_shadowmap)
    else:
        l = nodes['Begin'].outputs[0].links[0]
        links.remove(l)
        links.new(nodes['Begin'].outputs[0], nodes['Set Target Mesh'].inputs[0])

    if not cam.rp_worldnodes:
        relink('Draw World', 'Set Target Accum')

    if not cam.rp_translucency:
        relink('Set Target Accum', 'Draw Compositor + FXAA')

    if cam.rp_overlays:
        links.new(nodes['Draw Compositor + FXAA'].outputs[0], nodes['Clear Target Overlay'].inputs[0])

def make_deferred(cam):

    nodes['Begin'].inputs[1].default_value = cam.rp_hdr
    nodes['Screen'].inputs[0].default_value = int(cam.rp_supersampling)

    if cam.rp_shadowmap != 'None':
        n = nodes['Shadow Map']
        n.inputs[1].default_value = n.inputs[2].default_value = int(cam.rp_shadowmap)
    else:
        l = nodes['Loop Lamps'].outputs[1].links[0]
        links.remove(l)
        links.new(nodes['Loop Lamps'].outputs[1], nodes['Deferred Light'].inputs[0])

    # if not cam.rp_decals:
        # relink('Set Target.005', 'SSAO')

    if not cam.rp_ssao:
        relink('SSAO', 'Deferred Indirect')        
        l = nodes['Deferred Indirect'].inputs[3].links[0]
        links.remove(l)

    if not cam.rp_worldnodes:
        relink('Draw World', 'Set Target Accum')

    if not cam.rp_translucency:
        relink('Set Target Accum', 'Bloom')

    if not cam.rp_bloom:
        relink('Bloom', 'SSR')

    if not cam.rp_ssr:
        relink('SSR', 'Draw Compositor')

    if not cam.rp_compositornodes:
        pass

    last_node = 'Draw Compositor'
    if cam.rp_antialiasing == 'SMAA':
        last_node = 'SMAA'
    elif cam.rp_antialiasing == 'TAA':
        last_node = 'Copy'
        links.new(nodes['SMAA'].outputs[0], nodes['TAA'].inputs[0])
        links.new(nodes['Reroute.019'].outputs[0], nodes['SMAA'].inputs[5])
        links.new(nodes['gbuffer2'].outputs[0], nodes['GBuffer'].inputs[2])
        links.new(nodes['Reroute.014'].outputs[0], nodes['SMAA'].inputs[1])
    elif cam.rp_antialiasing == 'FXAA':
        last_node = 'FXAA'
        relink('SMAA', 'FXAA')
    elif cam.rp_antialiasing == 'None':
        last_node = 'Draw Compositor'
        l = nodes['Draw Compositor'].outputs[0].links[0]
        links.remove(l)
        links.new(nodes['Framebuffer'].outputs[0], nodes['Draw Compositor'].inputs[1])

    if cam.rp_overlays:
        links.new(nodes[last_node].outputs[0], nodes['Clear Target Overlay'].inputs[0])
