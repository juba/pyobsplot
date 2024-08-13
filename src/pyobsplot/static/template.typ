#let find-child(elem, tag) = {
  elem.children
    .find(e => "tag" in e and e.tag == tag)
}

#let decode-ampersand(text) = {
    let res = text.replace("&", "&#x26;")
    res
}


#let encode-xml(elem) = {
  if (type(elem) == "string") {
    decode-ampersand(elem)
  } else if (type(elem) == "dictionary") {
    "<" + elem.tag + elem.attrs.pairs().map(
        v => " " + v.at(0) + "=\"" + decode-ampersand(v.at(1)) + "\""
    ).join("") + if (elem.tag == "svg") {" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\""} + ">" + elem.children.map(encode-xml).join("") + "</" + elem.tag + ">"
  }
}

#let obsplot(
    file,
    margin: 10pt,
    font-family: ("San Francisco", "Segoe UI", "Noto Sans", "Roboto", "Cantarell", "Ubuntu", "Lucida Grande", "Arial"),
    scale: 1,
    legend-padding: 20,
) = {

    set text(
        font: font-family,
        fallback: true
    )

    let dpi = 100 / scale

    let swatch-item(elem) = {
        set align(horizon)
        stack(
            dir: ltr, 
            spacing: .2em, 
            image.decode(
                encode-xml(elem.children.first()), 
                width: 1in * int(elem.children.first().attrs.width) / dpi, 
                height: 1in * int(elem.children.first().attrs.width) /dpi
            ),
            text(elem.children.last(), size: 1in * 10/dpi)
        )
    }

    let swatch(elem) = {
        stack(
            dir: ltr, 
            spacing: .6em, 
            ..elem.children.filter(e => e.tag == "span").map(swatch-item)
        )
    }

    let html = xml(file)
    let figure = html.first()
    let bg_color = figure.attrs.typstbg
    let fg_color = figure.attrs.typstfg
    let caption_color = figure.attrs.typstcaption
    let title = find-child(figure, "h2")
    let subtitle = find-child(figure, "h3")
    let caption = find-child(figure, "figcaption")
    let figuresvgs = figure.children.filter(e => "tag" in e and e.tag == "svg")
    let legends = figuresvgs
    .filter(svg => "ramp" in svg.attrs.class)
    .map(svg => (..svg, attrs: (..svg.attrs,
                                 width: str(int(svg.attrs.width) + 2*legend-padding), 
                                 viewbox: "-"+str(legend-padding)+" 0 "+str(int(svg.attrs.width)+legend-padding)+" "+str(int(svg.attrs.height)))
                                ))
    let mainfigure = figuresvgs.find(svg => "ramp" not in svg.attrs.class)
    let figurewidth = calc.max(..figuresvgs.map(svg => int(svg.attrs.width)))

    set page(
        width: 1in*figurewidth/dpi + 2*margin,
        height: auto,
        margin: (x: margin, y: margin),
        fill: rgb(bg_color)
    )

    show heading.where(level: 1): set text(size: (1in * 20/dpi), weight: 600, fill: rgb(fg_color))
    show heading.where(level: 2): set text(size: (1in * 16/dpi), weight: 400, fill: rgb(fg_color))

    stack(
        dir: ttb,
        spacing: 1in * 6/dpi,
        if (title != none) {
            heading(title.children.first(), level: 1)
            v(1in * 8/dpi)
        },
        if (subtitle != none) {
            heading(subtitle.children.first(), level: 2)
            v(1in * 8/dpi)
        },
        ..figure.children.filter(e => e.tag == "div").map(swatch),
        ..legends.map(svg => image.decode(encode-xml(svg), height: 1in * int(svg.attrs.height) / dpi)),
        image.decode(encode-xml(mainfigure), height: 1in * int(mainfigure.attrs.height) / dpi),
        if (caption != none) {
            set text(size: 1in * 13/dpi, fill: rgb(caption_color), weight: 500)
            text(caption.children.first())
            v(1in * 4/dpi)
        }
    )
}