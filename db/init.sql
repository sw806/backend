CREATE TABLE IF NOT EXISTS pricepoint (
  _id SERIAL PRIMARY KEY,
  _time TIMESTAMP WITH TIME ZONE NOT NULL,
  _price DECIMAL NOT NULL
);
