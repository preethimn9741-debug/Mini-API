async function upload() {
    const file = document.getElementById("file").files[0];
    if (!file) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    alert(data.message);
}

async function validate() {
    const file = document.getElementById("file").files[0];
    if (!file) {
        alert("Please select a file");
        return;
    }

    const res = await fetch(`/validate?filename=${file.name}`, {
        method: "POST"
    });

    const data = await res.json();
    document.getElementById("result").innerText =
        "Errors found: " + data.total_errors;
}

function download() {
    window.location.href = "/download";
}
