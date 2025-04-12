// adapted from https://github.com/bigskysoftware/fixi

(() => {
	if (document.__mo) return
	document.__mo = new MutationObserver((recs) => recs.forEach((r) => r.type === "childList" && r.addedNodes.forEach((n) => process(n))))
	const dispatch = (elt, type, detail, bub) => elt.dispatchEvent(new CustomEvent("x:" + type, { detail, cancelable: true, bubbles: bub !== false, composed: true }))
	const transition = document.startViewTransition?.bind(document)
	const doSwap = (id, where, content) => {
		const target = document.getElementById(id)
		if (!target) throw new Error(`Target element with id "${id}" not found.`)
		if (where === "outerHTML") target.outerHTML = content
		else if (where === "innerHTML") target.innerHTML = content
		else if (where in target) target[where] = content
		else throw new Error(`Unsupported swap type "${where}".`)
	}
	const ws = new WebSocket(`${location.protocol.replace('http', 'ws')}//${location.host}/ws`)
	ws.onmessage = async (event) => {
		updates = JSON.parse(event.data)
		const promises = updates.map(async (update) => {
			const [type, id, where, content] = update
			if (type === "swap") return transition(() => doSwap(id, where, content)).finished
		})
		await Promise.all(promises)
	}
	let init_hdlr = (elt) => {
		if (elt.__hdlr) return
		elt.__hdlr_busy = false
		elt.__hdlr = async (evt) => {
			evt.preventDefault()
			if (elt.__hdlr_busy) return
			elt.__hdlr_busy = true
			const action = elt.getAttribute("x-handler")
			const form = elt.form || elt.closest("form")
			const body = new FormData(form ?? undefined, evt.submitter)
			if (!form && elt.name) body.append(elt.name, elt.value)
			const data = (body) ? Object.fromEntries(body) : {}
			ws.send(JSON.stringify({action,data}))
			elt.__hdlr_busy = false
		}
		elt.__hdlr.evt = elt.getAttribute("x-trigger") || (elt.matches("form") ? "submit" : elt.matches("input:not([type=button]),select,textarea") ? "change" : "click")
		elt.addEventListener(elt.__hdlr.evt, elt.__hdlr)
		dispatch(elt, "inited", {}, false)
	}
	let process = (n) => {
		if (!dispatch(n, "process", {})) return
		if (n.matches && n.matches("[x-handler]")) init_hdlr(n)
		if (n.querySelectorAll) n.querySelectorAll("[x-handler]").forEach(init_hdlr)
	}
	document.addEventListener("DOMContentLoaded", async () => {
		document.__mo.observe(document.documentElement, { childList: true, subtree: true })
		await new Promise((resolve, reject) => (ws.onopen = resolve, ws.onerror = reject))
		process(document.body)
	})
})()
