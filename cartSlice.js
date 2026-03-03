// src/cartSlice.js
import { createSlice } from "@reduxjs/toolkit";

const persisted = (() => {
  try {
    const raw = localStorage.getItem("cart");
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
})();

const initialState = {
  items: persisted,
};

const cartSlice = createSlice({
  name: "cart",
  initialState,
  reducers: {
    addToCart: (state, action) => {
      const existing = state.items.find((i) => i.id === action.payload.id);
      if (existing) {
        existing.quantity += action.payload.quantity;
      } else {
        state.items.push(action.payload);
      }
      try {
        localStorage.setItem("cart", JSON.stringify(state.items));
      } catch (e) {}
    },
    removeFromCart: (state, action) => {
      state.items = state.items.filter((i) => i.id !== action.payload);
      try {
        localStorage.setItem("cart", JSON.stringify(state.items));
      } catch (e) {}
    },
    clearCart: (state) => {
      state.items = [];
      try {
        localStorage.removeItem("cart");
      } catch (e) {}
    },
  },
});

export const { addToCart, removeFromCart, clearCart } = cartSlice.actions;
export default cartSlice.reducer;
