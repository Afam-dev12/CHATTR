const socket = io();

const input =
    document.getElementById("messageInput");

const messages =
    document.getElementById("messages");

const typingDiv =
    document.getElementById("typing");

socket.emit("join", {
    room: room
});

if (input) { 

    input.addEventListener("input", () => { 

        socket.emit("typing", { 
            username: currentUsername,
            room:room
        });
    });

    input.addEventListener("keypress", (e) => { 

        if (e.key === "Enter") {
            sendMessage();
        }
    });

}  

function sendMessage() {

    if (!input) return;

    const message = input.value.trim();

    if (message === "") return;

    socket.emit("send_message", { 
        sender_id: currentUserId,
        receiver_id: otherUserId,
        message: message,
        room: room
    });

    input.value = "";

}

socket.on("show_typing", (data) => { 

    typingDiv.innerText =
         `${data.username} is typing...`;

    setTimeout(() => { 

        typingDiv.innerText = "";

    }, 1500);

});

socket.on("receive_message", (data) => { 

    const wrapper = document.createElement("div");

    wrapper.classList.add("message-animation");

    if (data.sender_id == currentUserId) {

        wrapper.className += " flex justify-end";

        wrapper.innerHTML =`
           <div class="bg-blue-500 p-4 rounded-2xl max-w-[60%]">
               <p>${data.message}</p>

               <p class="text-xs mt-2 opacity-70">
                    Sent
               </p>
            </div>

        `;
    } else { 

        wrapper.className += " flex justify-start";

        wrapper.innerHTML =`
           <div class="bg-gray-800 p-4 rounded-2xl max-w-[60%]">
              <p>${data.message}</p>
            </div>
        `;
    }

    messages.appendChild(wrapper);

    messages.scrollTop = messages.scrollHeight;

});