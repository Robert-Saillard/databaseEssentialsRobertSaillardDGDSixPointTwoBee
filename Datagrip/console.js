use multimedia_db;

db.createCollection('sprites');
db.createCollection('audio');
db.createCollection('scores');

db.scores.insertOne({
  player_name: "Rick",
  score: 2000
})

db.audio.insertOne({
    filename: "wifikun.ogg",
    content: "Binary.createFromBase64('T2dnUwACAAAAAAAAAAAAAAABAAAAAAjn3kMBE09wdXNIZWFkAQIAAIC7AAAAAABPZ2dTAAAAAAAAAAAAAAAAAAEBAAAAcvVdhQEQ…', 0)\n"
})

db.sprites.insertOne({
    filename: "rick astley.jpeg",
    content: "Binary.createFromBase64('/9j/4AAQSkZJRgABAQEAAAAAAAD/4QAuRXhpZgAATU0AKgAAAAgAAkAAAAMAAAABAHAAAEABAAEAAAABAAAAAAAAAAD/2wBDAAoH…', 0)\n"
})