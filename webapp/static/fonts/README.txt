Drop the bundled web fonts here (woff2, SIL Open Font License):

  Newsreader.woff2       — https://fonts.google.com/specimen/Newsreader
  HankenGrotesk.woff2    — https://fonts.google.com/specimen/Hanken+Grotesk

Download the families, convert/rename to the two filenames above, and place
them in this folder. The @font-face rules in static/css/app.css already point
here.

Until the files are present, the app falls back to Georgia (serif) and the
system UI sans-serif, so every page still renders correctly and offline.
