class HTMLBuilder:
    def __init__(self):
        self.styles = ""
        self.body_content = ""

    def add_style(self, style):
        """Fügt dem HTML-Stil-Block einen neuen Stil hinzu."""
        self.styles += style

    def add_body_content(self, content):
        """Fügt dem HTML-Baum Inhalt hinzu."""
        self.body_content += content

    def get_html(self):
        """Gibt das vollständige HTML-Dokument zurück."""
        html_template = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resparry Pi Informationen</title>
            <style>
                /* Allgemeine Stile */
                {self.styles}
            </style>
        </head>
        <body>
            <!-- Hauptcontainer -->
            {self.body_content}
        </body>
        </html>
        """
        return html_template
