// plotly extension

document.addEventListener("x:process", (evt) => {
    const createOrUpdateFigure = (elt) => {
        const figData = JSON.parse(elt.textContent)
        elt.textContent = ''
        let plotDiv = document.getElementById(elt.id + '-figure')
        if (!plotDiv) {
            plotDiv = document.createElement('div')
            plotDiv.className = 'plotly-figure'
            plotDiv.id = elt.id + '-figure'
            elt.parentNode.insertBefore(plotDiv, elt.nextSibling)
        }
        Plotly.react(plotDiv, figData.data, figData.layout)
    }
    const updateLayout = (elt) => {
        const updates = JSON.parse(elt.textContent)
        elt.textContent = ''
        const plotDiv = document.getElementById(elt.id + '-figure')
        Plotly.relayout(plotDiv, updates)
    }
    const processPlotly = (elt) => {
        if (elt.tagName !== 'SCRIPT' || elt.type !== 'application/json') 
            throw new Error("x-plotly element should be a script of type application/json")
        const op = elt.getAttribute("x-plotly")
        if (op === "figure") createOrUpdateFigure(elt)
        else if (op === "update-layout") updateLayout(elt)
        else throw new Error(`unknown plotly op: ${op}`)
    }
    const elt = evt.target
    if (elt.matches && elt.matches("[x-plotly]")) processPlotly(elt)
    if (elt.querySelectorAll) elt.querySelectorAll("[x-plotly]").forEach(processPlotly) 
});