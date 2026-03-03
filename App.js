import React, { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import axios from "axios";

import Navbar from "./components/Navbar";
import ProductCard from "./components/ProductCard";
import Login from "./components/Login";
import Signup from "./components/Signup";
import ForgotPassword from "./components/ForgotPassword";
import Cart from "./components/Cart";
import Checkout from "./components/Checkout";

import { setProducts, reserveStock } from "./productSlice";

export default function App() {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);
  const products = useSelector((state) => state.product.products);
  const cartItems = useSelector((state) => state.cart.items);

  const [currentPage, setCurrentPage] = useState("login"); // "login" | "signup" | "forgot"
  const [forgotUsername, setForgotUsername] = useState(""); // ✅ NEW
  const [showCart, setShowCart] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  // Fetch products from backend
  const fetchProducts = async () => {
    try {
      const res = await axios.get("/api/products/");
      dispatch(setProducts(res.data));

      if (cartItems && cartItems.length > 0) {
        cartItems.forEach((it) => {
          dispatch(reserveStock({ id: it.id, amount: it.quantity }));
        });
      }
    } catch (err) {
      console.error("Failed to fetch products:", err);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // Filter products
  const filteredProducts = products.filter((p) => {
    const matchesCategory =
      selectedCategory === "All" ||
      p.category?.toLowerCase() === selectedCategory.toLowerCase();
    const matchesSearch = p.name.toLowerCase().includes(query.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const categories = [
    "All",
    ...Array.from(new Set(products.map((p) => p.category || "Uncategorized"))),
  ];

  // ---------- AUTH SCREENS ----------
  if (!user) {
    if (currentPage === "signup") {
      return <Signup switchToLogin={() => setCurrentPage("login")} />;
    }

    if (currentPage === "forgot") {
      return (
        <ForgotPassword
          username={forgotUsername}   // ✅ PASS USERNAME HERE
          switchToLogin={() => setCurrentPage("login")}
        />
      );
    }

    return (
      <Login
        switchToSignup={() => setCurrentPage("signup")}
        switchToForgot={(uname) => {
          setForgotUsername(uname);   // ✅ STORE USERNAME
          setCurrentPage("forgot");   // ✅ GO TO FORGOT PAGE
        }}
      />
    );
  }

  // ---------- LOGGED IN VIEW ----------
  return (
    <div>
      <Navbar openCart={() => setShowCart(true)} />

      <div className="container" style={{ position: "relative" }}>
        {showCheckout ? (
          <Checkout
            onBack={() => setShowCheckout(false)}
            onSuccess={fetchProducts}
          />
        ) : showCart ? (
          <Cart onBack={() => setShowCart(false)} />
        ) : (
          <>
            {/* Category Toolbar */}
            <div className="category-toolbar" style={{ marginBottom: "20px" }}>
              {categories.map((cat) => (
                <button
                  key={cat}
                  className={selectedCategory === cat ? "active" : ""}
                  onClick={() => setSelectedCategory(cat)}
                  style={{
                    marginRight: "10px",
                    padding: "8px 16px",
                    borderRadius: "5px",
                    border:
                      selectedCategory === cat
                        ? "2px solid #27ae60"
                        : "1px solid #ccc",
                    backgroundColor:
                      selectedCategory === cat ? "#27ae60" : "#fff",
                    color: selectedCategory === cat ? "#fff" : "#000",
                    cursor: "pointer",
                  }}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Search box */}
            <div style={{ textAlign: "center", marginBottom: "30px" }}>
              <input
                placeholder="Search products..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{
                  width: "100%",
                  maxWidth: "900px",
                  padding: "18px 20px",
                  fontSize: "20px",
                  borderRadius: "10px",
                  border: "2px solid #ccc",
                  outline: "none",
                }}
              />
            </div>

            {/* Product grid */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: "20px",
              }}
            >
              {filteredProducts.length > 0 ? (
                filteredProducts.map((p) => (
                  <ProductCard key={p.id} product={p} />
                ))
              ) : (
                <div
                  style={{
                    gridColumn: "1 / -1",
                    textAlign: "center",
                    height: "200px",
                    fontSize: "20px",
                    color: "#555",
                  }}
                >
                  No products found.
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
