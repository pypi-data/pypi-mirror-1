/**
  * Javascript code for managing menu forms
  */

function manageAddNewElement(data, textStatus) {
	if (data && data.response) {
		// TODO
	}
}

function newElementMenu(event) {
	var form = jq("#customize-factoriesmenu");
	var data = {'element-name': jq('#element-name').val(),
	            'element-descr': jq('#element-descr').val(),
	            'condition-tales': jq('#condition-tales').val(),
	            'element-tales': jq('#element-tales').val()};
	data['action'] = 'add';
	jq.post("@@customize-factoriesmenu", data, manageAddNewElement, type='json');
	event.preventDefault();
}

jq(document).ready(function () {
	jq("#add-new-element-menu").click(newElementMenu);
});