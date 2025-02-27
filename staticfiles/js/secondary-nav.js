// Handle category scrolling and active state
document.addEventListener('DOMContentLoaded', function() {
    // Get all filter links using consistent selector
    const filterLinks = document.querySelectorAll('.secondary-nav li a');
    
    // Get all filterable items
    const foodBoxes = document.querySelectorAll('.food-box');
    
    // Add click event to each filter link
    filterLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Get the clicked link's parent li
            const clickedLi = this.parentElement;
            
            // Remove active class from all li elements
            document.querySelectorAll('.secondary-nav li').forEach(li => {
                li.classList.remove('active');
            });
            
            // Add active class to the clicked li
            clickedLi.classList.add('active');

            // Get the filter text
            const filterText = this.textContent.trim().toLowerCase();

            // Filter food boxes
            foodBoxes.forEach(box => {
                const foodType = box.querySelector('.food-type').textContent.trim().toLowerCase();
                
                if (filterText === 'all') {
                    box.style.display = 'block';
                } else if (filterText === foodType) {
                    box.style.display = 'block';
                } else {
                    box.style.display = 'none';
                }
            });
        });
    });

    // Set initial active state to the first li
    const firstLi = document.querySelector('.secondary-nav li');
    if (firstLi) {
        firstLi.classList.add('active');
    }
});