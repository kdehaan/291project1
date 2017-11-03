-- Adapted from data prepared by Jeff Cho, jeff.cho@ualberta.ca

-- Schema: cid* (text), name (text), address(text), pwd (text)
INSERT INTO customers VALUES
    ("c0", "Oliver", "0000, 0 ave", "0pass"),
    ("c1", "Isabel", "1111, 1 ave", "1pass"),
    ("c2", "Zack", "2222, 2 ave", "2pass"),
    ("c3", "Erin", "3333, 3 ave", "3pass"),
    ("c4", "Hank", "4444, 4 ave", "4pass"),
    ("c5", "Sam", "5555, 5 ave", "5pass"),
    ("c6", "Gillian", "6666, 6 ave", "6pass"),
    ("c7", "Liam", "7777, 7 ave", "7pass"),
    ("c8", "Betty", "8888, 8 ave", "8pass");

-- Schema: cat* (char(3)), name (text)
INSERT INTO categories VALUES
    ("pro", "Produce"),
    ("dai", "Dairy"),
    ("bak", "Bakery"),
    ("del", "Deli"),
    ("mea", "Meat"),
    ("she", "Shelf"),
    ("tex", "Textiles"),
    ("oth", "Other"),
    
    
-- Schema: pid* (char(6)), name (text), unit (text), cat (char(3))
INSERT INTO products VALUES
    ("bak0", "Bread, White, Sliced", "ea", "bak"),
    ("bak1", "Bagel, Everything, 6-pack", "ea", "bak"),
    ("bak2", "Pitas, Whole Wheat, 8-pack", "ea", "bak"),
    ("pro0", "Garlic, 3-pack", "ea", "pro"),
    ("pro1", "Cucumber, English", "ea", "pro"),
    ("pro2", "Tomato, Vine-Ripened", "kg", "pro"),
    ("pro9", "Baby Bok Choy", "kg", "pro"),
    ("del0", "Prosciutto, Sliced", "kg", "del"),
    ("del1", "Gouda, Mild", "ea", "del"),
    ("del2", "Guanciale", "kg", "del"),
    ("del9", "Jarlsberg", "kg", "del"),
    ("mea0", "Chicken Breasts", "kg", "mea"),
    ("mea1", "Chicken Thighs", "kg", "mea"),
    ("mea2", "Applewood Bacon", "ea", "mea"),
    ("mea9", "Pork Belly", "ea", "mea"),
    ("she0", "Spaghetti, Whole Wheat", "ea", "she"),
    ("she1", "Mayonnaise, Half-Fat, Jar", "ea", "she"),
    ("she2", "Coke Zero, Bottled, 6-pack", "ea", "she"),
    ("dai0", "Milk, Whole, Jug", "ea", "dai"),
    ("dai1", "Greek Yogurt, 5%, Tub", "ea", "dai"),
    ("dai2", "Sour Cream, 2%, Tub", "ea", "dai"),
    ("tex0", "Socks, Ankle, 6-pack", "ea", "tex"),
    ("tex9", "Pants, Sweat", "ea", "tex"),
    ("oth1", "Gift Card, $20", "ea", "oth"),
    ("oth2", "Headphones", "ea", "oth"),
    ("oth9", "PlayStation 4", "ea", "oth");
    
-- Schema: sid* (int), pid* (char6), qty (int), uprice (real)
INSERT INTO carries VALUES
    /* Unique Stock Cases: T&T has two unique items */
    (3, "oth9", 5, 399.99),
    (7, "del9", 10, 8.99),
    (5, "mea9", 15, 3.99),
    (5, "pro9", 20, 1.99),

    (0, "bak0", 10, 3.29),
    (0, "bak1", 25, 4.99),
    (0, "bak2", 33, 5.99),
    (0, "del0", 50, 3.99),    
    (0, "mea1", 47, 12.99),
    (0, "mea2", 43, 6.99),
    (0, "dai0", 80, 5.29),
    (0, "dai1", 5, 5.89),
    (0, "dai2", 50, 3.99),
    (0, "tex0", 10, 6.99),
    
    (1, "bak0", 20, 3.99),
    (1, "bak1", 5, 5.99),
    (1, "bak2", 23, 5.99),
    (1, "mea1", 500, 11.23),
    (1, "mea2", 38, 7.27),
    (1, "dai1", 17, 5.99),

    (2, "del0", 5, 4.22),
    (2, "dai1", 12, 6.23),
    (2, "dai2", 33, 3.69),
    (2, "mea1", 56, 13.00),
    
    (3, "mea1", 99, 12.99),
    (3, "tex0", 12, 7.99),

    (4, "mea1", 17, 12.99),

    (6, "dai1", 99, 5.99),
    (6, "mea1", 200, 12.99),
    
    (7, "dai0", 23, 5.19),
    (7, "mea1", 20, 12.99),
    (7, "tex0", 200, 7.99);
    
    
-- Schema: sid* (int), name (text), phone (text), address (text)
INSERT INTO stores VALUES
    (0, "0store", "000-0000", "0000 0 st"),
    (1, "1store", "111-1111", "1111 1 st"),
    (2, "2store", "222-3333", "2222 2 st"),
    (3, "3store", "333-3333", "3333 3 st"),
    (4, "4store", "444-4444", "4444 4 st"),
    (5, "5store", "555-5555", "5555 5 st"),
    (6, "6store", "666-6666", "6666 6 st"),
    (7, "7store", "777-7777", "7777 7 st"),
    (8, "8store", "888-8888, "8888 8 st"),
    (9, "9store", "999-9999", "9999 9 st");
    
    
-- Schema: oid* (int), sid* (int), pid* (char6), qty (int), uprice (real)
INSERT INTO olines VALUES

    /* 1000: Same dairy, different stores */
    (1000, 0, "dai1", 1, 5.89),
    (1000, 2, "dai1", 1, 6.23),
    (1000, 4, "mea1", 2, 12.99),
    (1000, 7, "tex0", 1, 7.99),
    (1001, 0, "mea1", 1, 12.99),
    (1001, 7, "del9", 1, 7.99),
    
    /* 1010, 1011: All orders with one store, not Walmart*/
    (1010, 7, "mea1", 1, 12.99),
    (1010, 7, "tex0", 1, 7.99),
    (1010, 7, "del9", 1, 7.99),
    (1011, 7, "mea1", 1, 12.99),
    (1011, 7, "del9", 1, 7.99),

    /* 1020, 1021: Different dairy, different stores, different orders */    
    (1020, 6, "dai1", 2, 5.99),
    (1020, 7, "tex0", 1, 7.99),
    (1020, 7, "del9", 1, 7.99),
    (1021, 0, "dai2", 5, 3.99),
    
    /* 1030: All orders with one store, all one Walmart */
    (1030, 3, "mea1", 2, 12.99),
    (1030, 3, "tex0", 1, 7.99),
    (1030, 3, "del9", 1, 7.99),
    (1031, 3, "mea1", 1, 12.99),
    
    /* 1041: Different dairy, same store */
    (1040, 1, "mea1", 5, 11.23),
    (1040, 7, "tex0", 1, 7.99),
    (1041, 0, "dai0", 2, 5.29),
    (1041, 0, "dai1", 3, 5.89),
    (1041, 2, "mea1", 4, 13.00),
    (1041, 7, "del9", 1, 7.99),
    
    /* 1051, 1051: All orders with Walmart, two different locations */
    (1050, 3, "mea1", 1, 12.99),
    (1050, 6, "del2", 1, 7.99),
    (1050, 3, "tex0", 1, 7.99),
    (1051, 6, "mea1", 1, 12.99),
    (1051, 3, "del2", 1, 7.99),
    
    /* 1060: Different dairy, different stores */
    (1060, 0, "dai2", 2, 3.99),
    (1060, 7, "tex0", 1, 7.99),
    (1060, 7, "dai0", 1, 5.19),
    (1061, 0, "mea1", 1, 12.99),
    
    /* 1070: All orders with one store, not Walmart */
    (1070, 0, "mea1", 1, 11.23),
    (1070, 0, "tex0", 1, 6.99),
    (1071, 0, "mea1", 1, 11.23),
    (1072, 0, "del0", 2, 3.99),
    (1073, 0, "mea2", 5, 6.99),
    
    /* 1080: Every dairy, multiple stores */
    (1080, 0, "dai0", 1, 5.50),
    (1080, 1, "dai1", 1, 5.99),
    (1080, 2, "dai2", 1, 3.69),
    (1080, 0, "dai1", 2, 5.89),
    (1080, 0, "mea1", 1, 12.99),
    (1080, 7, "tex0", 1, 7.99),
    (1081, 0, "mea1", 1, 12.99),
    (1081, 7, "del9", 1, 7.99),
    
    /* All orders not with Walmart but not one store */
    (1090, 0, "mea1", 1, 1.99),
    (1090, 7, "tex0", 1, 1.99),
    (1091, 0, "mea1", 1, 1.99),
    (1092, 0, "mea1", 1, 1.99),
    (1092, 7, "del9", 1, 1.99);

