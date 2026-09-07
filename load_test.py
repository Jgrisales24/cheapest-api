import argparse
import asyncio
import csv
import json
import math
import time
import uuid
from copy import deepcopy
from datetime import datetime, timezone

import httpx


BASE_URL = "http://localhost:3000"

GET_PATH = "/logistics/tenderos/productos-disponibles"
POST_PATH = "/logistics/pedidos"

GET_PARAMS = {
    "tiendaId": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    "zona": "Zona Norte"
}


def percentile(values, p):
    """
    Calcula un percentil usando interpolación lineal.
    p debe estar entre 0 y 1.
    """
    if not values:
        return 0.0

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    lower_value = ordered[lower]
    upper_value = ordered[upper]

    return lower_value + (upper_value - lower_value) * (position - lower)


async def execute_request(client, endpoint, body_template=None):
    timestamp = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()

    status_code = 0
    error = ""

    try:
        if endpoint == "GET":
            response = await client.get(
                GET_PATH,
                params=GET_PARAMS
            )

        else:
            body = deepcopy(body_template)

            # Cada pedido debe tener identificador único.
            body["identificador"] = f"LOAD-{uuid.uuid4()}"

            # Fecha actual para cada pedido.
            body["fechaHoraCreacion"] = (
                datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            )

            response = await client.post(
                POST_PATH,
                json=body
            )

        status_code = response.status_code

        if status_code >= 400:
            error = response.text[:200].replace("\n", " ")

    except httpx.TimeoutException as exc:
        error = f"Timeout: {exc}"

    except httpx.RequestError as exc:
        error = f"Connection error: {exc}"

    except Exception as exc:
        error = f"Unexpected error: {exc}"

    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "timestamp_iso": timestamp,
        "status_code": status_code,
        "latency_ms": latency_ms,
        "error": error
    }


async def virtual_user(
    user_id,
    start_delay,
    end_time,
    client,
    endpoint,
    body_template,
    results
):
    # Hace que los usuarios entren progresivamente durante el ramp-up.
    await asyncio.sleep(start_delay)

    # Una vez activo, cada usuario continúa enviando solicitudes
    # hasta que termina el tiempo total del experimento.
    while time.perf_counter() < end_time:
        result = await execute_request(
            client,
            endpoint,
            body_template
        )

        results.append(result)


async def run_test(args):
    body_template = None

    if args.endpoint == "POST":
        if not args.body:
            raise ValueError(
                "Para POST debe proporcionar --body sample_body.json"
            )

        with open(args.body, "r", encoding="utf-8") as file:
            body_template = json.load(file)

        items = body_template.get("items", [])

        if len(items) <= 20:
            raise ValueError(
                "El body del POST debe contener más de 20 ítems."
            )

    output_file = args.out

    if output_file is None:
        output_file = (
            "results_get.csv"
            if args.endpoint == "GET"
            else "results_post.csv"
        )

    limits = httpx.Limits(
        max_connections=args.users,
        max_keepalive_connections=min(args.users, 1000)
    )

    timeout = httpx.Timeout(args.timeout)

    results = []

    # El experimento dura:
    # ramp-up + tiempo sosteniendo la carga.
    experiment_start = time.perf_counter()
    end_time = experiment_start + args.ramp_up + args.duration

    print()
    print("==========================================")
    print("       CHEAPEST LOAD TEST")
    print("==========================================")
    print(f"Endpoint:          {args.endpoint}")
    print(f"Usuarios máximos:  {args.users}")
    print(f"Ramp-Up:           {args.ramp_up} s")
    print(f"Duración estable:  {args.duration} s")
    print(f"Archivo salida:    {output_file}")
    print("==========================================")
    print()

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        limits=limits,
        timeout=timeout,
        trust_env=False
    ) as client:

        tasks = []

        for user_id in range(args.users):

            if args.users == 1:
                delay = 0
            else:
                delay = (
                    user_id / (args.users - 1)
                ) * args.ramp_up

            task = asyncio.create_task(
                virtual_user(
                    user_id,
                    delay,
                    end_time,
                    client,
                    args.endpoint,
                    body_template,
                    results
                )
            )

            tasks.append(task)

        await asyncio.gather(*tasks)

    experiment_end = time.perf_counter()
    elapsed = experiment_end - experiment_start

    # Guardar CSV
    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp_iso",
                "status_code",
                "latency_ms",
                "error"
            ]
        )

        writer.writeheader()

        for result in results:
            writer.writerow({
                "timestamp_iso": result["timestamp_iso"],
                "status_code": result["status_code"],
                "latency_ms": round(result["latency_ms"], 3),
                "error": result["error"]
            })

    total_requests = len(results)

    latencies = [
        result["latency_ms"]
        for result in results
    ]

    error_count = sum(
        1
        for result in results
        if result["status_code"] >= 400
        or result["status_code"] == 0
        or result["error"] != ""
    )

    if total_requests > 0:
        average_latency = sum(latencies) / total_requests
        p95 = percentile(latencies, 0.95)
        p99 = percentile(latencies, 0.99)
        error_percentage = (
            error_count / total_requests
        ) * 100
        throughput = total_requests / elapsed
    else:
        average_latency = 0
        p95 = 0
        p99 = 0
        error_percentage = 0
        throughput = 0

    print()
    print("==========================================")
    print("           RESULTADOS")
    print("==========================================")
    print(f"Endpoint:             {args.endpoint}")
    print(f"Total requests:       {total_requests}")
    print(f"Tiempo total:         {elapsed:.2f} s")
    print(f"Throughput:           {throughput:.2f} req/s")
    print(f"Latencia promedio:    {average_latency:.2f} ms")
    print(f"p95:                  {p95:.2f} ms")
    print(f"p99:                  {p99:.2f} ms")
    print(f"Errores:              {error_count}")
    print(f"Error %:              {error_percentage:.2f}%")
    print(f"CSV:                  {output_file}")
    print("==========================================")
    print()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Pruebas de carga para Cheapest"
    )

    parser.add_argument(
        "--endpoint",
        choices=["GET", "POST"],
        required=True
    )

    parser.add_argument(
        "--users",
        type=int,
        required=True
    )

    parser.add_argument(
        "--ramp-up",
        type=float,
        required=True
    )

    parser.add_argument(
        "--duration",
        type=float,
        required=True
    )

    parser.add_argument(
        "--body",
        type=str
    )

    parser.add_argument(
        "--out",
        type=str
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=30
    )

    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    asyncio.run(run_test(arguments))