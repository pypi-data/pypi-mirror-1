from tw.api import Widget, JSLink, CSSLink, js_callback
from tw import jquery

__all__ = ["Rating"]

rating_css = CSSLink(
    modname = __name__, 
    filename = 'static/ratings.css',)
rating_js = JSLink(
    modname = __name__, 
    filename = 'static/jquery.rating.js', 
    css=[rating_css],
    javascript=[jquery.packed])


class Rating(Widget):
    params = ["action", "average_text", "label_text", "submit_text", "on_click"]
    css_class = "rating"
    default = 0
    average_text = "Average Rating:"
    label_text = "Rate Me!"
    template = """\
<form class="${css_class}" title="${average_text} ${value}" 
      action="${action}" id="${id}">
    <label for="${id}_select" class="avg">${label_text}</label>
    <select id="${id}_select">
        <option value="0">0</option>
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
        <option value="5">5</option>
    </select>
    <input type="button" value="${submit_text}">
</form>"""

    javascript = [rating_js]
    include_dynamic_js_calls = True
    
    on_click = ''
    
    def update_params(self, d):
        super(Rating, self).update_params(d)
        self.add_call(jquery.function(js_callback(
            jquery.function('#'+d.id).rating()
            )))
