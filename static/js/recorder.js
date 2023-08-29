function recordData() {
        navigator
        .mediaDevices
        .getUserMedia({audio: true})
        .then(stream => { handlerFunction(stream) });

        function handlerFunction(stream) {
            rec = new MediaRecorder(stream);
            rec.mimeType = "audio/wav"
            rec.ondataavailable = e => {
                audioChunks.push(e.data);
                if (rec.state == "inactive") {
                    let blob = new Blob(audioChunks, {type: 'audio/wav'});
                    stream.getAudioTracks()[0].stop()
                    sendData(blob);
                }
            }

           rec.start();
    }

    }


    function sendData(data) {
        var form = new FormData();
        form.append('file', data, 'data.wav');
        form.append('title', 'data.wav');
        //Chrome inspector shows that the post data includes a file and a title.
        $.ajax({
            type: 'POST',
            url: '/transcribe',
            data: form,
            cache: false,
            processData: false,
            contentType: false,
            success: function(response){
                document.getElementById("transcript").innerHTML = JSON.stringify(response).transcript;}
        }).done(function(response) {
            console.log(data);
        });
    }

    recordButton.onclick = e => {
        recordButton.disabled = true;
        stopButton.disabled = false;
        audioChunks = [];
        recordData();
    };

    stopButton.onclick = e => {
        recordButton.disabled = false;
        stopButton.disabled = true;
        rec.stop();
    };