function hideForm(){
  $("#form-wrapper").slideUp();
}

function showAddContactForm(){
  $.get("@@addContact.html", function(data){
    $("#form-content").empty().append(data);
    $("#form-wrapper").slideDown();
    $("#zcontact-ContactAddForm").ajaxForm(function(){
      getSearchResults();
    });
    $("#form\\.widgets\\.newField").change(function(){
      alert('hurray');
      $("#zcontact-ContactAddForm").submit();
      });

  }
	)
}

function showSearchContactForm(){
  $.get("@@searchContacts.html", function(data){
    $("#form-content").empty().append(data);
    $("#form-wrapper").slideDown();
    $("#zcontact-ContactSearchForm").ajaxForm(function(data){
       $("#search-results").empty().append(data);
    });
  }
	)
}


function getSearchResults(){
  $.get("@@contacts.html", function(data){
    $("#search-results").empty().append(data);
  });
}

function initializeApp(){
  $("#form-wrapper").hide();
  $("#add-contact-button").click(showAddContactForm);
  $("#search-contact-button").click(showSearchContactForm);
  $("#form-hide-button").click(hideForm);
}


$(document).ready(function() {
   initializeApp();
});
