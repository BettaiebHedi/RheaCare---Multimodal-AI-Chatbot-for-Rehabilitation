const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
// const generatedImage = document.getElementById('generated-image');
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");

let userText = null;
// const API_KEY = "PASTE-YOUR-API-KEY-HERE"; // Paste your API key here

// const loadDataFromLocalstorage = () => {
//     // Load saved chats and theme from local storage and apply/add on the page
//     const themeColor = localStorage.getItem("themeColor");

//     document.body.classList.toggle("light-mode", themeColor === "light_mode");
//     themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";

//     const defaultText = `<div class="default-text">
//                             <h3><i class="bi bi-brain"></i> RhéCare Assitant </h3> <!-- Changed name and added an icon -->
//                             <img src="assets2/images/logos/loooogo.png" alt="RhéCare Assistant Logo" class="assistant-logo" /> <!-- Add image -->
//                             <p>Start a conversation and explore the power of AI.<br> Your chat history will be displayed here.</p>
//                         </div>`;

//     chatContainer.innerHTML = localStorage.getItem("all-chats") || defaultText;
//     chatContainer.scrollTo(0, chatContainer.scrollHeight); // Scroll to bottom of the chat container
// }



const createChatElement = (content, className) => {
    // Create new div and apply chat, specified class and set html content of div
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv; // Return the created chat div
}

// multimodel rag and sd
const getChatResponse = async (incomingChatDiv) => {
    const imgElement = document.createElement("img");
    const pElement=document.createElement("p");
    try {
        const response_sd = await fetch('/chat2/generate-image/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: userText })
        });

        if (!response_sd.ok) throw new Error('Image generation failed.');
        try {
            const data = await response_sd.json();
            imgElement.src = data.image_url;
            const response_retrieval = await fetch('/chat2/query/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: userText,image:imgElement.src })
            });

            if (!response_retrieval.ok) throw new Error('retrieval failed.');
            try {
                const data2 = await response_retrieval.json();
                const response_generation = await fetch('/chat2/rag/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: userText,image_url:imgElement.src,retrieved_docs:data2 })
                });
                if (!response_generation.ok) throw new Error('generation failed.');
                const data3 = await response_generation.json();
                imgElement.style.display = 'block';
                imgElement.style.width = '512px'; // Set the width
                imgElement.style.height = '512px'; // Set the height
                imgElement.style.marginLeft = '25px';
                pElement.textContent = data3.response;
            }catch(error){
                pElement.classList.add("error");
                pElement.textContent = "Oops! Something went wrong while retrieving the response. Please try again.";
            }
        }catch(error){
            pElement.classList.add("error");
            pElement.textContent = "Oops! Something went wrong while retrieving the response. Please try again.";
        }
    } catch (error) {
        pElement.classList.add("error");
        pElement.textContent = "Oops! Something went wrong while retrieving the response. Please try again.";
    }

    // Remove the typing animation, append the paragraph element and save the chats to local storage
    incomingChatDiv.querySelector(".typing-animation").remove();
    incomingChatDiv.querySelector(".chat-details").appendChild(imgElement);
    incomingChatDiv.querySelector(".chat-details").appendChild(pElement);
    localStorage.setItem("all-chats", chatContainer.innerHTML);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
}

const copyResponse = (copyBtn) => {
    // Copy the text content of the response to the clipboard
    const reponseTextElement = copyBtn.parentElement.querySelector("p");
    navigator.clipboard.writeText(reponseTextElement.textContent);
    copyBtn.textContent = "done";
    setTimeout(() => copyBtn.textContent = "content_copy", 1000);
}

// const showTypingAnimation = () => {
//     // Display the typing animation and call the getChatResponse function
//     const html = `<div class="chat-content">
//                     <div class="chat-details">
//                         <img src="/static/chat.png" alt="chatbot-img">
//                         <div class="typing-animation">
//                             <div class="typing-dot" style="--delay: 0.2s"></div>
//                             <div class="typing-dot" style="--delay: 0.3s"></div>
//                             <div class="typing-dot" style="--delay: 0.4s"></div>
//                         </div>
//                     </div>
//                     <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
//                 </div>`;
//     // Create an incoming chat div with typing animation and append it to chat container
//     const incomingChatDiv = createChatElement(html, "incoming");
//     chatContainer.appendChild(incomingChatDiv);
//     chatContainer.scrollTo(0, chatContainer.scrollHeight);
//     getChatResponse(incomingChatDiv);
// }

// const handleOutgoingChat = () => {
//     userText = chatInput.value.trim(); // Get chatInput value and remove extra spaces
//     if(!userText) return; // If chatInput is empty return from here

//     // Clear the input field and reset its height
//     chatInput.value = "";
//     chatInput.style.height = `${initialInputHeight}px`;

//     const html = `<div class="chat-content">
//                     <div class="chat-details">
//                         <img src="/static/avatar.png" alt="user-img">
//                         <p>${userText}</p>
//                     </div>
//                 </div>`;

//     // Create an outgoing chat div with user's message and append it to chat container
//     const outgoingChatDiv = createChatElement(html, "outgoing");
//     chatContainer.querySelector(".default-text")?.remove();
//     chatContainer.appendChild(outgoingChatDiv);
//     chatContainer.scrollTo(0, chatContainer.scrollHeight);
//     setTimeout(showTypingAnimation, 500);
// }

deleteButton.addEventListener("click", () => {
    // Remove the chats from local storage and call loadDataFromLocalstorage function
    if(confirm("Are you sure you want to delete all the chats?")) {
        localStorage.removeItem("all-chats");
        loadDataFromLocalstorage();
    }
});

themeButton.addEventListener("click", () => {
    // Toggle body's class for the theme mode and save the updated theme to the local storage 
    document.body.classList.toggle("light-mode");
    localStorage.setItem("themeColor", themeButton.innerText);
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
});

const initialInputHeight = chatInput.scrollHeight;

chatInput.addEventListener("input", () => {   
    // Adjust the height of the input field dynamically based on its content
    chatInput.style.height =  `${initialInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    // If the Enter key is pressed without Shift and the window width is larger 
    // than 800 pixels, handle the outgoing chat
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

loadDataFromLocalstorage();
sendButton.addEventListener("click", handleOutgoingChat);