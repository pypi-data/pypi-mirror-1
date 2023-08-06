/**
 * @author dave
 */
$(document).ready(function(){
	console.log("doc ready");
	tagModelFields();
	registerListeners();
	selectType();
	showSelectedModelOnly();
});

function registerListeners(){
	$("#id_type").bind("change", selectType);
	$("#id_model").bind("change", selectModel);
}

function tagModelFields(){
	console.log("tagging fields");
	//add a class to the divs that are model fields, making them easier to work with.
	$("select:not(#id_type, #id_model, #id_menus)").parent().parent().addClass("model_field");
}

function selectType(){
	var link_type = $("#id_type").val();
	if (link_type == 'internal'){
		//clear the external_url text field
		$("#id_external_url").val("");
		//hide external stuff
		$("div.external_url").hide("fast");
		
		//hide all model fields
		//$('div.model_field').hide("fast");
		showSelectedModelOnly();
		
	}
	else{
		//hide internal stuff
		$("div.model").hide("fast");
		$("select:not(#id_type, #id_menus)").parent().parent().hide("fast");
		//deselect any of the internals
		$("div.model_field").find("select").each(function(){
			$(this).val(0);
		});
		
		//deselect the model type
		$("#id_model").val(0);
		
		//show external stuff
		$("div.external_url").show("fast");
	}
}

function selectModel(){
	//deselect all model fields
	$("div.model_field").find("select").each(function(){
		$(this).val(0);
	});
	showSelectedModelOnly();
}

function showSelectedModelOnly(){
	//show the model choice field
	if ($("#id_type").val() == 'internal'){
		$("div.model").show("fast");
	}
	
	
	var model = $("#id_model").val().split(".")[1]; //example: page
	
	//hide all the other model fields
	$('div.model_field:not(.'+model+')').hide("fast");
	
	//show the selected model field
	$("div.model_field."+model).show("fast");
}


