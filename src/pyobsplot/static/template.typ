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
    margin: 4pt,
    font: "SF Pro Display",
    font-size: 10pt,
) = {
    let swatch-item(elem) = {
        set align(horizon)
        stack(
            dir: ltr, 
            spacing: .5em, 
            image.decode(
                encode-xml(elem.children.first()), 
                width: 1pt * int(elem.children.first().attrs.width), 
                height: 1pt * int(elem.children.first().attrs.width)
            ),
            text(elem.children.last())
        )
    }

    let swatch(elem) = {
        stack(
            dir: ltr, 
            spacing: 1em, 
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

    set text(
        font: "SF Pro Display",
        size: font-size,
        fallback: false
    )

    set page(
        width: 1pt*figurewidth + 2*margin,
        height: auto,
        margin: (x: margin, y: margin)
    )

    stack(
        dir: ttb,
        spacing: 1em,
        heading(title.children.first(), level: 1),
        if (subtitle != none) {
            heading(subtitle.children.first(), level: 2)
        },
        v(2em),
        ..figure.children.filter(e => e.tag == "div").map(swatch),
        image.decode(encode-xml(figuresvg)),
        if (caption != none) {
            text(caption.children.first())
        }
    )
}