(* Native test driver only; excluded from theorem implementations. *)
let () =
  try while true do
    let line = read_line () in
    let fields = List.filter (fun s -> s <> "") (String.split_on_char ' ' (String.trim line)) in
    match List.map int_of_string fields with
    | family :: style :: xs ->
        (match NativeExtract.entry family style xs with
         | None -> print_endline "FAIL"
         | Some ys -> print_endline (String.concat " " (List.map string_of_int ys)))
    | _ -> failwith "invalid native test record"
  done with End_of_file -> ()
