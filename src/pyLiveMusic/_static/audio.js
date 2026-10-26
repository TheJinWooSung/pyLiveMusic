const audio = document.getElementById("audio");
const volume = document.getElementById("volume");
const status = document.getElementById("status");

const roomId = window.location.pathname
    .split("/")
    .filter(Boolean)
    .pop();
const roomToken = window.location.hash.slice(1);

let peerConnection = null;
let serverPosition = 0;
let lastAllowedPosition = 0;
let serverPlaying = false;
let audioStarted = false;
let stateInterval = null;

audio.volume = 1;
audio.playbackRate = 1;
audio.defaultPlaybackRate = 1;


volume.addEventListener("input", () => {
    const value = Number(volume.value);

    if (
        Number.isFinite(value) &&
        value >= 0 &&
        value <= 1
    ) {
        audio.volume = value;
    }
});


audio.addEventListener("ratechange", () => {
    if (
        audio.playbackRate !== 1 &&
        !audio.dataset.syncing
    ) {
        audio.playbackRate = 1;
    }
});


audio.addEventListener("seeking", () => {
    if (!serverPlaying) {
        return;
    }

    if (
        Math.abs(
            audio.currentTime -
            lastAllowedPosition
        ) > 0.5
    ) {
        audio.currentTime =
            lastAllowedPosition;
    }
});


audio.addEventListener("pause", async () => {
    if (
        !audio.srcObject ||
        audio.ended ||
        !serverPlaying
    ) {
        return;
    }

    try {
        await audio.play();

        audioStarted = true;

    } catch {
        audioStarted = false;

        status.textContent =
            "CLICK PAGE TO START AUDIO";
    }
});


document.addEventListener("click", async () => {
    if (
        !audio.srcObject ||
        audioStarted ||
        !serverPlaying
    ) {
        return;
    }

    try {
        await audio.play();

        audioStarted = true;

        status.textContent = "LIVE";

    } catch (error) {
        console.warn(
            "[AUDIO] Playback failed:",
            error
        );
    }
});


async function connectWebRTC() {
    console.log("[WEBRTC] Connecting...");

    status.textContent =
        serverPlaying
            ? "CONNECTING"
            : "NOT PLAYING";

    peerConnection =
        new RTCPeerConnection({
            iceServers: [
                {
                    urls:
                        "stun:stun.l.google.com:19302"
                },
                {
                    urls:
                        "stun:stun.cloudflare.com:3478"
                }
            ]
        });


    peerConnection.addTransceiver(
        "audio",
        {
            direction: "recvonly"
        }
    );


    let peerId = null;
    const pendingCandidates = [];


    peerConnection.onicecandidate =
        async (event) => {
            if (
                !event.candidate ||
                !event.candidate.candidate
            ) {
                return;
            }

            console.log(
                "[WEBRTC] ICE candidate:",
                event.candidate.candidate
            );


            if (!peerId) {
                pendingCandidates.push(
                    event.candidate
                );

                return;
            }


            await sendCandidate(
                event.candidate
            );
        };


    async function sendCandidate(
        candidate
    ) {
        try {
            const response =
                await fetch(
                    `/api/rooms/${roomId}/webrtc/candidate`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${roomToken}`
                        },

                        body: JSON.stringify({
                            peer_id: peerId,

                            candidate:
                                candidate.toJSON()
                        })
                    }
                );


            if (!response.ok) {
                console.warn(
                    "[WEBRTC] Candidate rejected:",
                    await response.text()
                );
            }

        } catch (error) {
            console.warn(
                "[WEBRTC] Candidate failed:",
                error
            );
        }
    }


    peerConnection.ontrack =
        async (event) => {
            if (
                event.track.kind !==
                "audio"
            ) {
                return;
            }


            console.log(
                "[WEBRTC] Audio track received"
            );


            audio.srcObject =
                new MediaStream([
                    event.track
                ]);


            audio.volume =
                Number(volume.value);


            audio.playbackRate = 1;
            audio.defaultPlaybackRate = 1;


            if (!serverPlaying) {
                status.textContent =
                    "NOT PLAYING";

                return;
            }


            try {
                await audio.play();

                audioStarted = true;

                status.textContent =
                    "LIVE";

            } catch (error) {
                audioStarted = false;

                console.warn(
                    "[AUDIO] Autoplay blocked",
                    error
                );

                status.textContent =
                    "CLICK PAGE TO START AUDIO";
            }
        };


    peerConnection.onconnectionstatechange =
        () => {
            const state =
                peerConnection.connectionState;


            console.log(
                "[WEBRTC] Connection:",
                state
            );


            switch (state) {
                case "connected":
                    status.textContent =
                        serverPlaying
                            ? "LIVE"
                            : "NOT PLAYING";

                    break;


                case "connecting":
                    status.textContent =
                        "CONNECTING";

                    break;


                case "disconnected":
                    status.textContent =
                        "DISCONNECTED";

                    break;


                case "failed":
                    status.textContent =
                        "WEBRTC_FAILED";

                    break;


                case "closed":
                    status.textContent =
                        "CLOSED";

                    break;
            }
        };


    peerConnection.oniceconnectionstatechange =
        () => {
            console.log(
                "[WEBRTC] ICE:",
                peerConnection
                    .iceConnectionState
            );
        };


    peerConnection.onicecandidateerror =
        (event) => {
            console.warn(
                "[WEBRTC] ICE candidate error:",
                event
            );
        };


    peerConnection.onicegatheringstatechange =
        () => {
            console.log(
                "[WEBRTC] ICE gathering:",
                peerConnection
                    .iceGatheringState
            );
        };


    peerConnection.onsignalingstatechange =
        () => {
            console.log(
                "[WEBRTC] Signaling:",
                peerConnection
                    .signalingState
            );
        };


    const offer =
        await peerConnection.createOffer();


    await peerConnection.setLocalDescription(
        offer
    );


    console.log(
        "[WEBRTC] Sending offer..."
    );


    const response =
        await fetch(
            `/api/rooms/${roomId}/webrtc/offer`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${roomToken}`
                },

                body: JSON.stringify({
                    type:
                        peerConnection
                            .localDescription
                            .type,

                    sdp:
                        peerConnection
                            .localDescription
                            .sdp
                })
            }
        );


    if (!response.ok) {
        throw new Error(
            await response.text()
        );
    }


    const answer =
        await response.json();


    peerId =
        answer.peer_id;


    console.log(
        "[WEBRTC] Peer ID:",
        peerId
    );


    for (
        const candidate
        of pendingCandidates
    ) {
        await sendCandidate(
            candidate
        );
    }


    pendingCandidates.length = 0;


    await peerConnection.setRemoteDescription({
        type: answer.type,
        sdp: answer.sdp
    });


    console.log(
        "[WEBRTC] Remote description set"
    );
}


async function updateServerPosition() {
    try {
        const response =
            await fetch(
                `/api/rooms/${roomId}`,
                {
                    headers: {
                        "Authorization": `Bearer ${roomToken}`
                    }
                }
            );


        if (response.status === 404) {
            console.error(
                `[ROOM] Room ${roomId} does not exist`
            );


            status.textContent =
                "ROOM NOT FOUND";


            serverPlaying = false;


            stopStatePolling();


            return false;
        }


        if (!response.ok) {
            throw new Error(
                `Room request failed: ${response.status}`
            );
        }


        const data =
            await response.json();


        if (
            data.error ===
            "NOT_PLAYING_ANYTHING_CURRENTLY"
        ) {
            serverPlaying = false;
            audioStarted = false;

            status.textContent =
                "NOT PLAYING";

            return true;
        }


        serverPlaying = true;


        if (
            typeof data.position ===
            "number"
        ) {
            serverPosition =
                data.position;

            lastAllowedPosition =
                data.position;
        }


        return true;

    } catch (error) {
        console.error(
            "Could not get room state:",
            error
        );


        serverPlaying = false;


        status.textContent =
            "ROOM ERROR";


        stopStatePolling();


        return false;
    }
}


function stopStatePolling() {
    if (
        stateInterval !== null
    ) {
        clearInterval(
            stateInterval
        );

        stateInterval = null;
    }
}


async function initialize() {
    if (!roomId) {
        status.textContent = "INVALID ROOM";
        return;
    }

    if (!roomToken) {
        status.textContent = "OPEN THE PRIVATE PLAYER LINK";
        return;
    }


    const exists =
        await updateServerPosition();


    if (!exists) {
        return;
    }


    try {
        await connectWebRTC();

    } catch (error) {
        console.error(
            "[WEBRTC] Connection failed:",
            error
        );


        status.textContent =
            "WEBRTC_FAILED";


        stopStatePolling();


        return;
    }


    stateInterval =
        setInterval(
            updateServerPosition,
            2000
        );
}


initialize();
