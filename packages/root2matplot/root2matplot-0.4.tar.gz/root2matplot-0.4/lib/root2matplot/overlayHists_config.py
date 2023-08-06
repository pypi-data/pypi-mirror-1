"""
A default configuration file read by the overlaidHists script
"""

## When using matplotlib, all text from the first column will be replaced
## with the corresponding text in the second column for titles and labels;
## this is necessary to correctly transform ROOT's special LaTeX sytax into
## proper LaTeX sytax for use by matplotlib.

# Start from this one for default behavior
replace = [
    ('#eta'    , r'$\eta$'),
    ('#phi'    , r'$\phi$'),
    ('#Deltam' , r'$\Delta m$'),
    ('fb^{-1}' , r'$\text{fb}^{-1}$'),
    ('<'       , r'$<$'),
    ('>'       , r'$>$'),
    ('#'       , r''),
    ]

# Start from this one if you're using the 'text.usetex' rc setting; it uses
# more extensive LaTeX commands since it's actually using TeX for rendering
## replace = [
##     ('pt'      , r'$p_\text{T}$'),
##     ('pT'      , r'$p_\text{T}$'),
##     ('p_{T}'   , r'$p_\text{T}$'),
##     ('#eta'    , r'$\eta$'),
##     ('#phi'    , r'$\phi$'),
##     ('#Deltam' , r'$\Delta m$'),
##     ('fb^{-1}' , r'$\text{fb}^{-1}$'),
##     ('<'       , r'$<$'),
##     ('>'       , r'$>$'),
##     ('#'       , r''),
##     ]

colors = [
    ## a default set of contrasting colors the author happens to like
    ( 82, 124, 219), # blue
    (212,  58, 143), # red
    (231, 139,  77), # orange
    (145,  83, 207), # purple
    (114, 173, 117), # green
    ( 67,  77,  83), # dark grey
    ]

markers_matplotlib = [
    'o', 's', '^', 'x', '*', 'D', 'h', '1'
    ]

markers_root = [
    ## This default set mirrors the matplotlib markers above
     4, # circle 
    25, # square
    26, # triangle
     5, # x
    30, # five-pointed star
    27, # diamond
    28, # cross
     3, # asterisk
    ]
