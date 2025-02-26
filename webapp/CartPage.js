import React from 'react';
import { Link } from 'react-router-dom';

const CartPage = ({ cart }) => {
  return (
    <div className="cart-page">
      <h1>Your Cart</h1>
      <Link to="/" className="back-button">
        ← Back to Home
      </Link>
      <div className="cart-items">
        {cart.length > 0 ? (
          cart.map((item, index) => (
            <div key={index} className="cart-item">
              <h3>{item.name}</h3>
              <p>Dosage: {item.dosage_instructions}</p>
              <p>Quantity: {item.dosage_count}</p>
              <p>Status: {item.status}</p>
            </div>
          ))
        ) : (
          <p>Your cart is empty.</p>
        )}
      </div>
    </div>
  );
};

export default CartPage;