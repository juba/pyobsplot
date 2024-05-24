#let find-child(elem, tag) = {
  elem.children
    .find(e => "tag" in e and e.tag == tag)
}

#let encode-xml(elem) = {
  if (type(elem) == "string") {
    elem
  } else if (type(elem) == "dictionary") {
    "<" + elem.tag + elem.attrs.pairs().map(
        v => " " + v.at(0) + "=\"" + v.at(1) + "\""
    ).join("") + if (elem.tag == "svg") {" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\""} + ">" + elem.children.map(encode-xml).join("") + "</" + elem.tag + ">"
  }
}

#let obsplot(
    file,
    margin: 10pt,
    font-family: ("San Francisco", "Segoe UI", "Noto Sans", "Roboto", "Cantarell", "Ubuntu", "Lucida Grande", "Arial"),
    scale: 1
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
    let title = find-child(figure, "h2")
    let subtitle = find-child(figure, "h3")
    let caption = find-child(figure, "figcaption")
    let figuresvg = find-child(figure, "svg")
    let figurewidth = int(figuresvg.attrs.width)

    set page(
        width: 1in*figurewidth/dpi + 2*margin,
        height: auto,
        margin: (x: margin, y: margin)
    )

    show heading.where(level: 1): set text(size: (1in * 20/dpi), weight: 600)
    show heading.where(level: 2): set text(size: (1in * 16/dpi), weight: 400)

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
        image.decode(encode-xml(figuresvg)),
        if (caption != none) {
            set text(size: 1in * 13/dpi, fill: rgb(85, 85, 85), weight: 500)
            text(caption.children.first())
            v(1in * 4/dpi)
        }
    )
}