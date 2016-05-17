Adding fonts involves 4 steps:

1. Add the font file to static/fonts folder or static/fonts/nonfree in `.woff` `.woff2` `.ttf` or `.otf` format.
2. Add an entry to `static/fonts/fonts.json` under `families`.

You can see what @font-face rules have been created by inspecting
`static/css/fonts/fonts-auto.scss`, variable declarations are also defined.


Deploying fonts to the server involves two additional steps

3. The changes to fonts.json should be commited to git and pushed.
4. The invoke task `invoke deploy.production.push_fonts` should be used.


# More Details

## Automatic Conversion

Any font files in any format placed in this folder will be automatically
converted to woff and woff2, and given cache-busting names and @font-face rules
in accordance with the contents of fonts.json

## fonts.json

fonts.json contains a list of families which tells the server what to do, an entry like this:

```"source-sans-pro": "Source Sans Pro"```

Means that the file source-sans-pro should be used to define a @font-face 
rule with a font family called "Source Sans Pro"

The alternative entry looks like this:
```
"noto-sans-jp": [
    {
        "var": "noto-sans-jp",
        "name": "Noto Sans Jp",
        "subset": "jp"
    }
    ...
```
 
This means that upon encountering a font starting with "noto-sans-jp" it
will be subsetted to only those glyphs found in the language `jp`, this 
subsetting is also bold and italic aware.

In addition `"subset": ["zh", "lzh"]` can be used to to create a subset
based on multiple texts. `"subset": "\*"` will subset based on all glyphs,
the lack of subsetting instructions means no subsetting will be performed at all
and unused glyphs may be included in the resulting font. It is reasonable
to not perform subsetting if we can reasonably expect to use most of the
glyphs in the font.

## Variables

Variables are also added to fonts-auto.scss, such as:
$noto-sans-jp: 'Noto Sans JP';

The variable can be used in place of the family name in font-family. Using
the variable can be preferable because if you misspell the variable name
the scss compiler will fail noisily, on the other hand if you use the font
name and make a typo the result will be silent failure as the browser
can't find the named font, and falls back to another.


