// js helpers for minisite

AddSkinProperties = function() {
   jq("#portal-globalnav li:last").addClass('last');
   jq('#portal-searchbox .searchButton').val('OK');
   jq('#portal-columns td:first').addClass('firstColumn');
   if (jq("#portal-column-two").length) jq("#portal-column-two").addClass('lastColumn');
   else jq("#portal-column-content").addClass('lastColumn');
}

jq(document).ready(AddSkinProperties);
