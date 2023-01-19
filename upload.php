<?php
$targetPath = "uploads/" . basename($_FILES["inpFile"]["name"]); //Undefined array key 'inpFile', the $_FILES array is null 
//this means the HTTP POST method is not sending the file here....
$uploaded = move_uploaded_file($_FILES["inpFile"]["tmp_name"], $targetPath);
print($uploaded)
?>
