// src/productSlice.js
import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  products: [], // {id, name, category, price, stock}
};

const productSlice = createSlice({
  name: "product",
  initialState,
  reducers: {
    setProducts: (state, action) => {
      state.products = action.payload;
    },
    addProduct: (state, action) => {
      state.products.push(action.payload);
    },
    removeProduct: (state, action) => {
      state.products = state.products.filter(p => p.id !== action.payload);
    },
    decreaseStock: (state, action) => {
      const { id, amount } = action.payload;
      const p = state.products.find((x) => x.id === id);
      if (p) {
        p.stock = Math.max(0, (p.stock || 0) - (amount || 1));
      }
    },
    increaseStock: (state, action) => {
      const { id, amount } = action.payload;
      const p = state.products.find((x) => x.id === id);
      if (p) {
        p.stock = (p.stock || 0) + (amount || 1);
      }
    },
    reserveStock: (state, action) => {
      // consumes stock for persisted cart items on app load
      const { id, amount } = action.payload;
      const p = state.products.find((x) => x.id === id);
      if (p) {
        p.stock = Math.max(0, (p.stock || 0) - (amount || 0));
      }
    },
  },
});

export const {
  setProducts,
  addProduct,
  removeProduct,
  decreaseStock,
  increaseStock,
  reserveStock,
} = productSlice.actions;
export default productSlice.reducer;
