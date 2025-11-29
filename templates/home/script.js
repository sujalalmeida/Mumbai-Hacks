// const steps = document.querySelectorAll('.form-step');
//   const progressItems = document.querySelectorAll('.progress-item');

//   let currentStep = 0;

//   function showStep(step) {
//     steps.forEach((s, index) => {
//       s.classList.toggle('active', index === step);
//     });

//     progressItems.forEach((item, index) => {
//       item.classList.toggle('active', index === step);
//       item.classList.toggle('completed', index < step);
//     });
//   }

//   // Navigation listeners
//   document.getElementById('step1-next')?.addEventListener('click', () => {
//     currentStep = 1;
//     showStep(currentStep);
//   });

//   document.getElementById('step2-prev')?.addEventListener('click', () => {
//     currentStep = 0;
//     showStep(currentStep);
//   });

//   document.getElementById('step2-next')?.addEventListener('click', () => {
//     currentStep = 2;
//     showStep(currentStep);
//   });

//   // Repeat for other steps as needed:
//   // Example:
//   document.getElementById('step3-prev')?.addEventListener('click', () => {
//     currentStep = 1;
//     showStep(currentStep);
//   });

//   document.getElementById('step3-next')?.addEventListener('click', () => {
//     currentStep = 3;
//     showStep(currentStep);
//   });
document.addEventListener("DOMContentLoaded", () => {
    const steps = document.querySelectorAll(".form-step");
  
    let currentStep = 0;
  
    function showStep(stepIndex) {
      steps.forEach((step, index) => {
        step.classList.toggle("active", index === stepIndex);
      });
    }
  
    // Step 1 to Step 2
    document.getElementById("step1-next").addEventListener("click", () => {
      currentStep = 1;
      showStep(currentStep);
    });
  
    // Step 2 back to Step 1
    document.getElementById("step2-prev").addEventListener("click", () => {
      currentStep = 0;
      showStep(currentStep);
    });
  
    // Step 2 to Step 3
    document.getElementById("step2-next").addEventListener("click", () => {
      currentStep = 2;
      showStep(currentStep);
    });
  });
  