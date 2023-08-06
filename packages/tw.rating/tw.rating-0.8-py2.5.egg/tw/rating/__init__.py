from tw.api import Widget, JSLink, CSSLink, js_callback
from tw import jquery

__all__ = ["Rating"]

rating_css = CSSLink(
    modname = __name__, 
    filename = 'static/ratings.css')

rating_js = JSLink(
    modname = __name__, 
    filename = 'static/jquery.rating.js', 
    css=[rating_css],
    javascript=[jquery.jquery_js])


class Rating(Widget):
    params = ["action", "average_text", "label_text", "submit_text", "on_click"]
    css_class = "rating"
    default = 0

    average_text = "Average Rating:"
    average_text__doc = \
        "The text you'd like to appear as the average rating's label"

    label_text = "Rate Me!"
    label_text__doc = "The label for the select menu"

    submit_text = "Rate"
    submit_text__doc = "The text on the submit button"

    action = ""
    action__doc = "Where the rating should be POSTed"

    on_click = ""
    on_click__doc = "The js to be run when a json reponse is recieved"

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
</form>
<script type="text/javascript">
    function ${id}_callback_handler(response)
    {
        ${on_click}
    }
    (function($){

    $('#${id}').rating();

    })(jQuery);
</script>
"""
    javascript = [rating_js]
    include_dynamic_js_calls = True

    def update_params(self, d):
        super(Rating, self).update_params(d)
