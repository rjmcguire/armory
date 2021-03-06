
def tesc_levels(tesc):
    tesc.write('if (gl_InvocationID == 0) {')
    tesc.write('    gl_TessLevelInner[0] = innerLevel;')
    tesc.write('    gl_TessLevelInner[1] = innerLevel;')
    tesc.write('    gl_TessLevelOuter[0] = outerLevel;')
    tesc.write('    gl_TessLevelOuter[1] = outerLevel;')
    tesc.write('    gl_TessLevelOuter[2] = outerLevel;')
    tesc.write('    gl_TessLevelOuter[3] = outerLevel;')
    tesc.write('}')

def interpolate(tese, var, size, normalize=False, declare_out=False):
    vec = 'vec{0}'.format(size)
    if declare_out:
        tese.add_out('{0} {1}'.format(vec, var))

    tese.write('{0} {1}_0 = gl_TessCoord.x * tc_{1}[0];'.format(vec, var))
    tese.write('{0} {1}_1 = gl_TessCoord.y * tc_{1}[1];'.format(vec, var))
    tese.write('{0} {1}_2 = gl_TessCoord.z * tc_{1}[2];'.format(vec, var))
    
    prep = ''
    if not declare_out:
        prep = vec + ' '

    if normalize:
        tese.write('{0}{1} = normalize({1}_0 + {1}_1 + {1}_2);'.format(prep, var))
    else:
        tese.write('{0}{1} = {1}_0 + {1}_1 + {1}_2;'.format(prep, var))
