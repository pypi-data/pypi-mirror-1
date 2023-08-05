<div xmlns:py="http://purl.org/kid/ns#">
    <table>
        <tr py:for="key in upc.keys()">
            <td>${key}</td>
            <td>${upc[key]}</td>
        </tr>
    </table>
</div>