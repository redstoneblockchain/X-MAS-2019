 <?php
if (isset ($_GET['source'])) {
    show_source ("index.php");
    die ();
}
?>

<head>
    <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<form class="center">
    <h2>Cobalt Inc. employee database search</h2>
    <label>Name:</label>
    <input type="text" name="name" autocomplete="off">
    <input type="submit" value="Search">
</form>
<br>
<!-- ?source=1 -->

<?php
include ("config.php");
$conn = new mysqli ($servername, $username, $password, $dbname);

if (isset ($_GET['name'])) {
    $name = $_GET['name'];
    $name = str_replace ("*", "", $name);
    $records = mysqli_query ($conn, "SELECT * FROM users WHERE name=/*" . $name . "*/ 'Geronimo'", MYSQLI_USE_RESULT); // Don't tell boss

    if ($records === false) {
        die ("<p>Our servers have run into a query error. Please try again later.</p>");
    }

    echo '<table>';
    echo '
    <tr>
        <th>Name</th>
        <th>Description</th>
    </tr>';

    while ($row = mysqli_fetch_array ($records, MYSQLI_ASSOC)) {
        echo '<tr>
            <td>',$row["name"],'</td>
            <td>',$row["description"],'</td>
        </tr>';
    }

    echo '</table>';
}
?>

</body>

