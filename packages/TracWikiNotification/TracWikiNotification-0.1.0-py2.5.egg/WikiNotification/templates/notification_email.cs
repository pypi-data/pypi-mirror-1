<?cs if:action == 'added' ?>
Added page "<?cs var:name ?>" by <?cs var:author ?> from <?cs var:ip ?>*
Page URL: <<?cs var:link ?>>
<?cs if:comment
?>Comment: <?cs var:comment ?><?cs /if ?>
Content:

<?cs var:text ?>

<?cs elif:action == 'modified' ?>

Changed page "<?cs var:name ?>" by <?cs var:author ?> from <?cs var:ip ?>*
Page URL: <<?cs var:link ?>>
Diff URL: <<?cs var:linkdiff ?>>
Revision <?cs var:version ?><?cs if:comment ?>
Comment: <?cs var:comment ?><?cs /if ?>

<?cs if:wikidiff==''
?>Changes on attached <?cs var:name ?>.diff file.<?cs
elif:wikidiff!=''
?>-------8<------8<------8<------8<------8<------8<------8<------8<--------
<?cs var:wikidiff ?>
-------8<------8<------8<------8<------8<------8<------8<------8<--------<?cs
 /if ?>

<?cs elif:action == 'deleted' ?>
Deleted page "<?cs var:name ?>" by <?cs var:author ?> from <?cs var:ip ?>*

<?cs elif:action == 'deleted_version' ?>
Page URL: <<?cs var:link ?>>
Deleted version "<?cs var:version ?>" of page "<?cs var:name ?>" by <?cs
var:author ?> from <?cs var:ip ?>*

<?cs /if ?>
* The IP shown here might not mean anything if the user is behind a proxy.

--
<?cs var:project.name ?> <<?cs var:project.url ?>>
<?cs var:project.descr ?>

This is an automated message. Someone at <?cs var:project.url ?>
added your email address to be notified of changes on <?cs var:project.name ?>.
If it was not you, please report to <?cs var:project.url ?>.
