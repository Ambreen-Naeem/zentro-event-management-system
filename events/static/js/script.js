document.addEventListener('DOMContentLoaded', () => {
    console.log("JS loaded: Zentro");
});
<form method="POST">
  {% csrf_token %}
  {{ form.as_p }}

  <p>Price: $<span id="ticket-price">0.00</span></p>

  <button type="submit">Register & Purchase Ticket</button>
</form>

<script>
const prices = {{ ticket_prices|safe }};
const select = document.querySelector('select[name="ticket_type"]');
const priceSpan = document.getElementById('ticket-price');

select.addEventListener('change', function() {
    priceSpan.textContent = prices[this.value];
});
</script>
