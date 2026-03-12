# Quick HTML Update - Set Default Model Display
**Purpose:** Update HTML interface to show llama3.1:8b as default model

This will add a simple JavaScript at page load to initialize the model labels to llama3.1:8b instead of "Loading..."

Add this script before the closing body tag in agentic_interface_enhanced.html:

```html
<script>
// Initialize default model labels
document.addEventListener('DOMContentLoaded', function() {
  const defaultModel = 'ollama:llama3.1:8b';
  const agents = ['monitor', 'analyzer', 'alert', 'predictor', 'coordinator'];
  
  agents.forEach(agent => {
    const label = document.getElementById(`current-model-${agent}`);
    if (label) {
      label.innerHTML = `🔹 Model: <strong>${defaultModel}</strong>`;
    }
  });
  
  console.log('✅ Default models set to llama3.1:8b');
});
</script>
```

OR better yet - add this to the existing page initialization to update the labels dynamically!
