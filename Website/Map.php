<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Historical Marine Traffic</title>
    <link rel="stylesheet" href="CSS/Main.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
    crossorigin=""></script>
</head>
<body>
    <div class="wrapper panel-open">
        <div class="panel">
            <H1 class="title">Historical Marine Traffic</H1>
            <form class="search">
                <input class="search-bar" placeholder="Search" name="search">
                <button class="search-submit">
                    <img class="button-icon" src="Images/search.png" alt="Search">
                </button>
            </form>
            <button class="map button" type="button">
                <img class="button-icon" src="Images/map.png" alt="Map Filter">
                <H2 class="button-text">Map Filters</H2>
            </button>
            <button class="vessel button" type="button">
                <img class="button-icon" src="Images/vessel.png" alt="Vessel Filter">
                <H2 class="button-text">Vessel</H2>
            </button>
            <button class="landmark button" type="button">
                <img class="button-icon" src="Images/landmark.png" alt="Landmark Filter">
                <H2 class="button-text">Landmark</H2>
            </button>
            <button class="map button" type="button">
                <img class="button-icon" src="Images/settings.png" alt="Map Filter">
                <H2 class="button-text">Map Settings</H2>
            </button>
            <button class="timeline button" type="button">
                <img class="button-icon" src="Images/timeline.png" alt="Timeline Filter">
                <H2 class="button-text">Timeline</H2>
            </button>
        </div>
        <button class="panel-toggle" type="button">
            <p class="material-icon icon-open"><<</p>
            <p class="material-icon icon-close">>></p>
        </button>
    </div>
    <div id="map"></div>
    <script>
        document.querySelector(".panel-toggle").addEventListener("click", () => {
        document.querySelector(".wrapper").classList.toggle("panel-open");
        });
    </script>
    <script>
        var coordinates = <?php
        $serverName = "DESKTOP-15B5442";
        $connectionInfo = array("Database"=>"Database", "UID"=>"IIS", "PWD"=>"AutoDriveSecond!001");

        /* Open the connection. */
        $connection = sqlsrv_connect($serverName, $connectionInfo);
        if($connection === false) {
            die(print_r(sqlsrv_errors(), true));
        }

        /* Set up and execute the query. */
        $sql = "SELECT Port.Latitude,
                       Port.Longitude
                FROM dbo.Port";

        $query = sqlsrv_query($connection, $sql);

        if($query === false) {
            die(print_r(sqlsrv_errors(), true));
        }

        if(sqlsrv_fetch($query) === false) {
            die(print_r(sqlsrv_errors(), true));
        }

        $coorindates = array();
        while($row = sqlsrv_fetch_array($query, SQLSRV_FETCH_ASSOC)) {
            array_push($coorindates, array("Latitude" => $row['Latitude'],
                                           "Longitude" => $row['Longitude']));
        }

        /* Close the connection. */
        sqlsrv_close($connection);
        echo json_encode($coorindates, JSON_HEX_TAG);
        ?>;

        var map = L.map('map').setView([55, -5], 6);

        var tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        {
            maxZoom: 15,
            attribution: '© OpenStreetMap'
        }).addTo(map);

        for (var i = 0; i < coordinates.length; i++) {
            var coordinate = coordinates[i];

            var marker = L.marker([coordinate['Latitude'], coordinate['Longitude']]).addTo(map);
        }
    </script>
</body>
</html>