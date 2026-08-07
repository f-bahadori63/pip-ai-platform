import { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard() {

  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {

    console.log("Loading dashboard...");

    api
      .get("/dashboard/executive/1")
      .then((response) => {

        console.log("DASHBOARD DATA:", response.data);

        setData(response.data);

      })
      .catch((err) => {

        console.error("DASHBOARD ERROR:", err);

        setError(err.message);

      });

  }, []);


  if (error) {

    return (
      <div>
        Dashboard Error:
        <br />
        {error}
      </div>
    );

  }


  if (!data) {

    return (
      <div>
        Loading dashboard...
      </div>
    );

  }


  return (

    <div>

      <h1>
        PIP Executive Dashboard
      </h1>


      <p>
        Project ID: {data.project_id}
      </p>


      <p>
        Health: {data.health?.status}
      </p>


      <p>
        Planned: {data.progress?.planned}%
      </p>


      <p>
        Actual: {data.progress?.actual}%
      </p>


      <p>
        Variance: {data.progress?.variance}%
      </p>


      <hr />


      <h3>
        Schedule
      </h3>

      <p>
        Health: {data.schedule?.health}
      </p>

      <p>
        Delay Index: {data.schedule?.delay_index}
      </p>

      <p>
        Critical Items: {data.schedule?.critical_items}
      </p>


      <hr />


      <h3>
        Recovery
      </h3>

      <p>
        Required: {String(data.recovery?.required)}
      </p>

      <p>
        Priority: {data.recovery?.priority}
      </p>


    </div>

  );

}