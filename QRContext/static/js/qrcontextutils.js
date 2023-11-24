let courseTimeoutId;
let usersTimeoutId;
let msgTimeoutId;
let userId;
let roomName;
let roomId;
let roomType;
let CheckedIn = false;
let checkedInRoomName;
let checkedInRoomId;
let checkedInRoomType;
let eventsList = [];
let enrolledCourses = [];
let lastQRCode;

// Function to handle hash changes
function handleHashChange() {
  // Get the current hash
  var currentHash = window.location.hash;

  // Check if the hash is #messages
  if (currentHash === "#messages") {
    // Show the content for the #messages stage
    messageFunction();
  } else {
    mainScreenFunction();
  }
}

function handleLogIn() {
  // Make an AJAX GET request
  $.ajax({
    type: "GET",
    url: `http://127.0.0.1:5000/API/checkin/${userId}`,
    async: false, // This makes the request synchronous
  })
    .done(function (response) {
      // Handle the successful response here
      console.log("Response:", response);
      if (response.checkin) {
        CheckedIn = response.checkin;
        console.log(CheckedIn);
        lastQRCode = response.checkin;
        handleQRCodeData(response.checkin);
        checkedInRoomName = roomName;
        checkedInRoomId = roomId;
        checkedInRoomType = roomType;

        $("#checkinBtn").hide();
        $("#checkoutBtn").show();
        $("#checked_in").text(`User Checked In ${checkedInRoomName}.`);
        $("#checked_in").show();
        // only show if restaurant
        if (response.checkin.split("/")[0] === "menu") {
          $("#container-eval").show();
        } else {
          $("#messageBtn").show();
        }
      } else {
        $("#checkoutBtn").hide();
      }
    })
    .fail(function (error) {
      // Handle errors here
      console.error("Error:", error);
    });

  // GET enrolled courses
  $.ajax({
    type: "GET",
    url: `http://127.0.0.1:5000/API/person/courses`,
    async: false, // This makes the request synchronous
  })
    .done(function (data) {
      for (course of data.enrolments) {
        dict = {
          id: course.id,
          name: course.name,
        };
        enrolledCourses.push(dict);
      }
      console.log(enrolledCourses);
    })
    .fail(function (error) {
      console.error("Error:", error);
    })
    .always(function () {
      let courseSelect = document.getElementById("sp-courseSelect");
      while (courseSelect.length > 1) {
        courseSelect.remove(1);
      }

      for (let course of enrolledCourses) {
        let option = document.createElement("option");
        option.text = course.name;
        courseSelect.add(option);
      }
    });
}

function handleQRCodeData(data) {
  $.ajax({
    url: "/API/QRCodeReader/" + data,
    type: "GET",
    async: false,
  })
    .done(function (data) {
      console.log(data);
      roomName = data.name;
      roomId = data.id;
      console.log(roomName, roomId);
      clearTimeout(courseTimeoutId);
      $("#coursesContainer").hide();
      $("#spContainer").hide();
      if (data.type === "menu") {
        roomType = "RESTAURANT";
        updateTableMenu(data);
        if (!CheckedIn) {
          $("#checkinBtn").show();
        }
      } else if (data.type === "ROOM") {
        roomType = data.type;
        updateTableSchedule(data);
      } else {
        roomType = data.type;
        $("#checkinBtn").hide();
        $("#calendar").hide();
        $("#menu").hide();
        handleStudyPeriodContainer();
      }
    })
    .fail(function (error) {
      console.error(error.statusText, ":", error.responseText);
    });
}

// Function to update the table with data
function updateTableMenu(data) {
  $("#calendar").hide();
  const dataTable = $("#dataTable");
  const nameHeader = $("#nameHeader");

  nameHeader.text("Menu of Restaurant: " + data.name);

  const tbody = dataTable.find("tbody");
  tbody.empty(); // Clear existing rows

  for (const food of data.food) {
    const row = $("<tr>").appendTo(tbody);
    $("<td>").text(food).appendTo(row);
  }

  $("#menu").show();
}

// Function to update the table with data
function updateTableSchedule(data) {
  $("#menu").hide();
  $("#checkinBtn").hide();

  $("#space-name").text(data["name"]);
  const scheduleBody = document.getElementById("schedule-body");
  scheduleBody.innerHTML = "";

  eventsList = data["events"] ? data["events"] : [];

  for (let hour = 8; hour < 20; hour++) {
    const min = ["00", "30"];

    for (let m = 0; m < 2; m++) {
      const row = document.createElement("tr");

      const headCol = document.createElement("td");
      headCol.classList.add("headcol");
      headCol.textContent =
        m === 0 ? `${hour.toString().padStart(2, "0")}:${min[m]}` : "";
      row.appendChild(headCol);

      const days = ["segunda", "terça", "quarta", "quinta", "sexta"];

      days.forEach((day) => {
        const cell = document.createElement("td");
        if (hour === 19 && m === 1) {
          cell.classList.add("final");
        }

        const divEvent = document.createElement("div");
        divEvent.classList.add("event");
        const pEvent = document.createElement("p");

        for (let event of eventsList) {
          if (event["weekday"] === day) {
            if (
              event["start"] ===
                `${hour.toString().padStart(2, "0")}:${min[m]}` &&
              event["end"] ===
                `${(hour + m).toString().padStart(2, "0")}:${
                  min[m === 0 ? 1 : 0]
                }`
            ) {

              pEvent.textContent = `${event['course']['acronym']} : ${event['info']}`;
              divEvent.appendChild(pEvent);
              cell.appendChild(divEvent);
              break;
            } else if (
              event["start"] === `${hour.toString().padStart(2, "0")}:${min[m]}`
            ) {
              divEvent.classList.add("init");

              pEvent.textContent = `${event['course']['acronym']} : ${event['info']}`;
              divEvent.appendChild(pEvent);
              cell.appendChild(divEvent);
              break;
            } else if (
              event["start"] <
                `${hour.toString().padStart(2, "0")}:${min[m]}` &&
              event["end"] >
                `${(hour + m).toString().padStart(2, "0")}:${
                  min[m === 0 ? 1 : 0]
                }`
            ) {
              divEvent.classList.add("cont");
              cell.appendChild(divEvent);
              break;
            } else if (
              event["start"] <
                `${hour.toString().padStart(2, "0")}:${min[m]}` &&
              event["end"] ===
                `${(hour + m).toString().padStart(2, "0")}:${
                  min[m === 0 ? 1 : 0]
                }`
            ) {
              divEvent.classList.add("end");
              cell.appendChild(divEvent);
              break;
            }
          }
        }

        row.appendChild(cell);
      });

      scheduleBody.appendChild(row);
    }
  }

  $("#calendar").show();
  if (!CheckedIn) {
    checkNextCourse();
  }
}

function checkNextCourse() {
  const date = new Date();
  // date.setHours(10, 50); // FIXM E erase after debug
  // date.setDate(27); // FIXM E erase after debug
  const weekday = date.getDay();
  console.log("weekday: " + weekday);
  const time = date.toTimeString().slice(0, 5);
  console.log("time: " + date.toTimeString().slice(0, 8));

  const days = ["", "segunda", "terça", "quarta", "quinta", "sexta", ""];
  let enrolled = false;
  const coursesNames = document.getElementById("courses-names");
  coursesNames.innerHTML = "";
  for (let event of eventsList) {
    let sHour = parseInt(event["start"].slice(0, 2));
    let sMin = parseInt(event["start"].slice(3)) - 15;
    if (sMin < 0) {
      sHour -= 1;
      sMin += 60;
    }
    let start = `${sHour.toString().padStart(2, "0")}:${sMin
      .toString()
      .padStart(2, "0")}`;

    let end = event.end;

    if (event["weekday"] === days[weekday] && start <= time && time < end) {

      if (enrolledCourses.some(course => course.id == event.course.id)) {
        enrolled = true;
        let p = document.createElement("p");
        p.classList = ["m-0"];
        p.textContent = event["course"]["name"] + " (" + event["info"] + ")";
        coursesNames.appendChild(p);
      }
    }
  }
  console.log(enrolled);
  if (enrolled && !CheckedIn) {
    $("#coursesContainer").show();
  }
  courseTimeoutId = setTimeout(() => {
    checkNextCourse();
  }, 10000);
}

function handleStudyPeriodContainer() {
  $("#sp-room").html(roomName);
  if (CheckedIn === lastQRCode) {
    $("#sp-formContainer").hide();
    $("#sp-warning").hide();
    $("#sp-success").show();
  } else if (!CheckedIn) {
    $("#sp-success").hide();
    $("#sp-warning").hide();
    $("#sp-courseSelect").prop("selectedIndex", 0);
    $("#sp-formContainer").show();
    $("#sp-form").removeClass("was-validated");
  } else {
    $("#sp-formContainer").hide();
    $("#sp-success").hide();
    $("#sp-warning").show();
  }
  $("#spContainer").show();
}

function mainScreenFunction() {
  $("#messagesContainer").hide();
  $("#mainScreenBtn").hide();
  if (CheckedIn && checkedInRoomType !== "RESTAURANT") {
    $("#messageBtn").show();
  }
  $("#checkBtns").show();
  $("#mainScreen").show();

  clearTimeout(usersTimeoutId);
  clearTimeout(msgTimeoutId);
}

function messageFunction() {
  $("#checkBtns").hide();
  $("#mainScreen").hide();
  $("#messageBtn").hide();
  $("#mainScreenBtn").show();

  $("#msg-userSelect").prop("disabled", true);
  $("#msg-roomId").text(checkedInRoomName);
  handleUserSelectUpdate();

}

// Common logic for updating users and managing the select element
function handleUserSelectUpdate() {
  updateUsers();
  // Add a change event listener to the <select> element
  $("#msg-userSelect").change(msgUserSelect);
  msgUserSelect();
  $("#messagesContainer").show();
}

function updateUsers() {
  // ajax to receive users on this room and update options on #msg-userSelect
  $.ajax({
    url: "/API/spaces/" + checkedInRoomId + "/users",
    type: "GET",
  })
    .done(function (data) {
      console.log(data);

      let userSelect = document.getElementById("msg-userSelect");
      const lastSelect = userSelect.value;
      while (userSelect.length > 1) {
        userSelect.remove(1);
      }

      for (let user of data) {
        if (user !== userId) {
          let option = document.createElement("option");
          option.text = user;
          userSelect.add(option);
        }
      }

      userSelect.value = lastSelect;
      $("#msg-userSelect").prop("disabled", false);
    })
    .fail(function (error) {
      console.error(error.statusText, ":", error.responseText);
    });

  usersTimeoutId = setTimeout(() => {
    updateUsers();
  }, 10000);
}

function msgUserSelect() {
  // Get the selected value
  const user = $("#msg-userSelect").val();
  clearTimeout(msgTimeoutId);
  if (user == "Select a user") {
    $("#msg-input-text").prop("disabled", true);
    $("#msg-input-btn").prop("disabled", true);
    $("#msg-chat").html("");
  } else {
    $("#msg-input-text").prop("disabled", false);
    $("#msg-input-btn").prop("disabled", false);

    // Update with the messages
    getMessages(user);
  }
  const textarea = document.getElementById("msg-input-text");
  textarea.value = "";
  textareaAutoResize(textarea);
}

function getMessages(other_user) {
  $.ajax({
    url: "/API/messages",
    type: "GET",
    data: {
      other_user: other_user,
    },
  })
    .done(function (data) {
      let messagesList = data;
      console.log(messagesList);

      $("#msg-chat").html("");
      for (let msg of messagesList) {
        let type = other_user == msg["from"] ? "received" : "sent";
        createMessage(type, msg["message"], msg["datetime"]);
      }
    })
    .fail(function (error) {
      console.error(error.statusText, ":", error.responseText);
    });

  msgTimeoutId = setTimeout(() => {
    getMessages(other_user);
  }, 10000);
}

function createMessage(type, message_text, time) {
  let message = document.createElement("message-container");
  message.setAttribute("type", type);
  message.setAttribute("message-text", message_text);
  message.setAttribute("time", time);

  let msgChat = document.getElementById("msg-chat");
  msgChat.appendChild(message);
}

function sendMessage() {
  const to_user = $("#msg-userSelect").val();
  const message = $("#msg-input-text").val();
  const dataToSend = {
    to: to_user,
    message: message,
  };

  $.ajax({
    url: "/API/messages",
    type: "POST",
    data: JSON.stringify(dataToSend), // Convert data to JSON string
    contentType: "application/json", // Set content type to JSON
  })
    .done(function (data) {
      console.log(data);
      const textarea = document.getElementById("msg-input-text");
      textarea.value = "";
      textareaAutoResize(textarea);
      createMessage("sent", data["message"], data["datetime"]);
    })
    .fail(function (error) {
      console.error(error.statusText, ":", error.responseText);
    });
}

function textareaAutoResize(textarea) {
  const maxHeight = 12 + 5 * parseFloat(getComputedStyle(textarea).lineHeight);
  let scrollHeight = textarea.scrollHeight;
  if (scrollHeight > maxHeight) {
    textarea.style.height = maxHeight + "px";
    textarea.style.overflowY = "scroll";
    textarea.style.removeProperty("border-radius");
  } else {
    for (let l = 1; l < 6; l++) {
      let height = 12 + l * parseFloat(getComputedStyle(textarea).lineHeight);
      let scrollHeight = textarea.scrollHeight;
      if (scrollHeight >= height) {
        textarea.style.height = height + "px";
      }
    }
    textarea.style.overflowY = "hidden";
  }
}
