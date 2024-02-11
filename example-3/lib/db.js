import React from "react";
import { MongoClient } from "mongodb";

const AksesDB = "mongodb://localhost:27017/ilham";

const options = {
  useNewUrlParser: true,
  useUnifiedTopology: true,
};

let client;
let database;

export default ConnectDB = async () => {
  {
    if (!client) {
      client = new MongoClient(AksesDB, options);
      await client.connect();
      database = client.db();
    }
    return database;
  }
};
