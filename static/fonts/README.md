Fonts are not stored in the git repository, use invoke tasks to
synchronize them with the server.

Any font files in any format placed in this folder will be automatically
converted to woff and woff2, and given names and @font-face rules
in accordance with the contents of fonts.json

fonts.json contains a list of families,

an entry like this:

```"source-sans-pro": "Source Sans Pro"```

Means that the file source-sans-pro should be used to define a @font-face rule with a font family called "Source Sans Pro"

The alternative entry looks like this:
```
"noto-sans-cjk": [
    {
        "var": "noto-sans-ko",
        "name": "Noto Sans Ko",
        "subset": "ko"
    }
    ...
```
 
This means that upon encountering a font starting with "noto-sans-cjk" it will be subsetted to only those glyphs found in the language `ko` (if the font file is bold, the subset will be only those glyphs which are ko and bold), the output file will be named "noto-sans-ko..." and a @font-face rule will be created allowing "Noto Sans Ko" (or $noto-sans-ko) to be used to refer to the subset.

`"subset": ["zh", "lzh"]` can be used to refer to create a subset based on multiple texts. `"subset": "*"` will subset based on all glyphs
