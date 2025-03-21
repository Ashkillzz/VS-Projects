const WScript = require("wscript-shell"); // Load Windows Script Shell

function exportFormData(pdfPath, xmlPath) {
    try {
        const acrobat = new ActiveXObject("AcroExch.App");
        const avDoc = new ActiveXObject("AcroExch.AVDoc");

        console.log("Opening PDF:", pdfPath);
        if (avDoc.Open(pdfPath, "")) {
            const pdDoc = avDoc.GetPDDoc();
            const jso = pdDoc.GetJSObject();

            console.log("Exporting form data to XML...");
            jso.exportAsXFDF(xmlPath);

            console.log("✅ Form data exported successfully to:", xmlPath);

            // Cleanup
            pdDoc.Close();
            avDoc.Close(true);
        } else {
            console.log("❌ Failed to open PDF.");
        }

        acrobat.Exit();
    } catch (error) {
        console.error("❌ Error:", error.message);
    }
}

// Set your file paths (update these)
const pdfPath = "D:\Aswin\VS Projects\Files\PDF Files\[12-12-2024]_Form_AOC-4-12122024_signed_2.pdf";  // Update with your PDF path
const xmlPath = "D:\Aswin\VS Projects\data.xml"; // Update with your XML save path

exportFormData(pdfPath, xmlPath);
