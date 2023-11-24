function handleCheckOutBtn(lastQRCode) {
   // Make an AJAX POST request
  $.ajax({
    type: "POST",
    url: "http://127.0.0.1:5000/API/checkout",
      })
    .done(function (data) {
      // Handle the successful response here
      console.log("Check-out successful:", data);
      CheckedIn = false;
      $("#checked_in").text(`User Checked Out.`);
      $("#checkoutBtn").hide();
      if (roomType === "RESTAURANT") {
        $("#checkinBtn").show();
      } else if (roomType === "ROOM") {
        checkNextCourse();
      } else {
        handleStudyPeriodContainer();
      }

      $("#container-eval").hide();
      $("#messageBtn").hide();
    })
    .fail(function (error) {
      console.error(error.statusText, ":", error.responseText);
    });
}

function handleCheckInBtn(lastQRCode, userId) {
  // Create a data object with the required JSON structure
  var data = {
    roomId: lastQRCode,
  };

  // Make an AJAX POST request
  $.ajax({
    type: "POST",
    url: "http://127.0.0.1:5000/API/checkin/" + userId,
    data: JSON.stringify(data), // Convert data to JSON string
    contentType: "application/json", // Set content type to JSON
  })
    .done(function (data) {
      CheckedIn = lastQRCode;
      console.log(CheckedIn);
      handleQRCodeData(lastQRCode);
      console.log("Check-in successful:", data);
      checkedInRoomName = roomName;
      checkedInRoomId = roomId;
      checkedInRoomType = roomType;

      $("#checkinBtn").hide();
      $("#checkoutBtn").show();
      $("#checked_in").text(`User Checked In ${checkedInRoomName}.`);
      if (lastQRCode.split("/")[0] === "menu") {
        $("#container-eval").show(); // only show if restaurant
      } else {
        $("#messageBtn").show();
        $("#coursesContainer").hide();
        clearTimeout(courseTimeoutId);
      }
      $("#checked_in").show();
    })
    .fail(function (error) {
      // Handle errors here
      console.error(error.statusText, ":", error.responseText);
    });
}

function handleRatingForm(resId = CheckedIn) {
  console.log(userId);
  // Get the values of input fields
  var evaluation = $("#evaluation").val();
  var rating = $('input[name="rating"]:checked').val();
  // Display values in the console
  console.log("userId: " + userId);
  console.log("resId: " + resId);
  console.log("Evaluation: " + evaluation);
  console.log("Rating: " + rating);

  dataToSend = {
    resId: resId,
    userId: userId,
    eval: evaluation,
    rating: rating,
  };
  $.ajax({
    url: "/API/evaluation",
    type: "POST",
    data: JSON.stringify(dataToSend), // Convert data to JSON string
    contentType: "application/json", // Set content type to JSON
  })
    .done(function (data) {
      console.log(data);
      $("#container-eval").hide();
      $("#eval-success").show();
      setTimeout(() => {
        $("#eval-success").hide();
      }, 5000);
    })
    .fail(function (error) {
      console.error(error.statusText, ":", error.responseText);
      $("#eval-fail").show();
      setTimeout(() => {
        $("#eval-fail").hide();
      }, 5000);
    });
}
