print '{'

def parse(fname):
    with open(fname) as f:
        first = True
        for line in f:
            if first:
                first = False
            else:
                print '    },'
            name, team, pos, cost = line.rstrip().split(', ')
            pid = name + '!' + team
            print '    "{}": {{'.format(pid)
            print '        "pid": "{}",'.format(pid)
            print '        "name": "{}",'.format(name)
            print '        "team": "{}",'.format(team)
            print '        "pos": "{}",'.format(pos)
            print '        "cost": {},'.format(int(float(cost) * 10))
            print '        "py/object": "util.Player"'

first = True
for fname in ['goalkeepers', 'defenders', 'midfielders', 'forwards']:
    if first:
        first = False
    else:
        print '    },'
    parse(fname)

print '    }'
print '}'
