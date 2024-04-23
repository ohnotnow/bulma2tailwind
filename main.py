import os
import datetime
import concurrent.futures
from gepetto import gpt, ollama, groq
from yaspin import yaspin

system_prompt = """
You are a helpful AI assistant who is an expert in converting between BulmaCSS and modern TailwindCSS.  The user will
provide you with a Laravel Blade template written in BulmaCSS, and you will convert it to TailwindCSS.  You will need to
make sure that the converted template is still functional and that all the necessary classes are included.  You will also
need to make sure that the converted template is as clean and readable as possible.  Example input and output is below.
You MUST respond with just the updated template code - no explanation or additional text is allowed.

---

Example Input:

<div class="field has-addons">
    <div class="control">
        <a class="button is-static">Date</a>
    </div>

    <div class="control">
        <label for="start_date" class="label sr-only">Start date</label>
        @if($edit === true)
        <input readonly class="input" id="start_date" name="start_date" value="{{ old('start_date', $booking->start->format('d/m/Y')) }}">
        @else
        <input class="input" id="start_date" name="start_date" value="{{ old('start_date', $booking->start->format('d/m/Y')) }}" v-pikaday>
        @endif
    </div>
    <div class="control">
        <a class="button is-static"> Start Time (15m steps)</a>
    </div>
    <div class="control">
        <label for="start_time" class="label sr-only">Start time</label>
        @if($edit === true)
        <input readonly class="input" type="time" id="start_time" name="start_time" value="{{ old('start_time', $booking->start->format('H:i')) }}" step="900">
        @else
        <input class="input" type="time" id="start_time" name="start_time" value="{{ old('start_time', $booking->start->format('H:i')) }}" step="900">
        @endif
    </div>
    <div class="control">
        <a class="button is-static"> End Time (15m steps)</a>
    </div>
    <div class="control">
        <label for="end_time" class="label sr-only">End time</label>
        @if($edit === true)
        <input readonly class="input" type="time" id="end_time" name="end_time" value="{{ old('end_time', $booking->end->format('H:i')) }}" step="900">
        @else
        <input class="input" type="time" id="end_time" name="end_time" value="{{ old('end_time', $booking->end->format('H:i')) }}" step="900">
        @endif
    </div>
</div>
<div class="field">
    <sample-select :samples='@json(auth()->user()->recentSamples)' :multiple="true" :preselected='@json(old("sample_ids", $booking->samples ? $booking->samples->pluck('id')->values() : []))'></sample-select>
</div>

@if ($equipment->usesPreciousMetals())
    <div class="mb-4">
        @livewire('booking-metals-editor', ['booking' => $booking, 'equipment' => $booking->equipment ?? $equipment, 'oldSessionMetals' => old('metals')])
    </div>
@endif


<div class="field">
    <div class="control">
        <label for="notes" class="label">Notes</label>
        @if($edit === true)
        <textarea readonly name="notes" id="notes" class="textarea">{{ old('notes', $booking->notes) }}</textarea>
        @else
        <textarea name="notes" id="notes" class="textarea">{{ old('notes', $booking->notes) }}</textarea>
        @endif
    </div>
</div>

---

Example Output:
<div class="flex flex-col space-y-4">
    <div class="flex space-x-2 items-center">
        <span class="bg-gray-200 px-2 py-1">Date</span>
        <div class="flex flex-col">
            <label for="start_date" class="sr-only">Start date</label>
            @if($edit === true)
            <input type="text" readonly class="border p-2" id="start_date" name="start_date" value="{{ old('start_date', $booking->start->format('d/m/Y')) }}">
            @else
            <input type="text" class="border p-2" id="start_date" name="start_date" value="{{ old('start_date', $booking->start->format('d/m/Y')) }}" v-pikaday>
            @endif
        </div>
        <span class="bg-gray-200 px-2 py-1">Start Time (15m steps)</span>
        <div class="flex flex-col">
            <label for="start_time" class="sr-only">Start time</label>
            @if($edit === true)
            <input type="time" readonly class="border p-2" id="start_time" name="start_time" value="{{ old('start_time', $booking->start->format('H:i')) }}" step="900">
            @else
            <input type="time" class="border p-2" id="start_time" name="start_time" value="{{ old('start_time', $booking->start->format('H:i')) }}" step="900">
            @endif
        </div>
        <span class="bg-gray-200 px-2 py-1">End Time (15m steps)</span>
        <div class="flex flex-col">
            <label for="end_time" class="sr-only">End time</label>
            @if($edit === true)
            <input type="time" readonly class="border p-2" id="end_time" name="end_time" value="{{ old('end_time', $booking->end->format('H:i')) }}" step="900">
            @else
            <input type="time" class="border p-2" id="end_time" name="end_time" value="{{ old('end_time', $booking->end->format('H:i')) }}" step="900">
            @endif
        </div>
    </div>

    <div>
        <sample-select :samples='@json(auth()->user()->recentSamples)' :multiple="true" :preselected='@json(old("sample_ids", $booking->samples ? $booking->samples->pluck('id')->values() : []))'></sample-select>
    </div>

    @if ($equipment->usesPreciousMetals())
    <div class="mb-4">
        @livewire('booking-metals-editor', ['booking' => $booking, 'equipment' => $booking->equipment ?? $equipment, 'oldSessionMetals' => old('metals')])
    </div>
    @endif

    <div class="flex flex-col">
        <label for="notes" class="font-bold">Notes</label>
        @if($edit === true)
        <textarea readonly name="notes" id="notes" class="border p-2">{{ old('notes', $booking->notes) }}</textarea>
        @else
        <textarea name="notes" id="notes" class="border p-2">{{ old('notes', $booking->notes) }}</textarea>
        @endif
    </div>
</div>
"""

def talk_to_openai(bot, messages):
    return bot.chat(messages, model="gpt-3.5-turbo")

def convert_template(filename):
    print(f"Converting {filename}...")
    bot = gpt.GPTModelSync()
    with open(filename, "r") as file:
        template = file.read()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Could you convert this BulmaCSS laravel blade template to use modern TailwindCSS?\n\n```{template}```"},
        ]
        response = talk_to_openai(bot, messages)
        updated_template = response.message
        # ensure all directories in the full fulename exist before writing it
        os.makedirs(os.path.dirname(f"tw/{filename}"), exist_ok=True)
        with open(f"tw/{filename}", "w") as file:
            file.write(updated_template)
        return f"tw/{filename}", response.cost

def process_file(filename):
    _, cost = convert_template(filename)
    return cost

def main():
    if not os.path.exists("tw"):
        os.makedirs("tw")
    total_cost = 0
    start_time = datetime.datetime.now()
    file_list = []
    for root, dirs, files in os.walk("."):
        for filename in files:
            if filename.endswith(".blade.php"):
                full_path = os.path.join(root, filename)
                full_path = full_path[2:]
                file_list.append(full_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        costs = executor.map(process_file, file_list)

    total_cost = sum(costs)
    end_time = datetime.datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()
    print(f"\n\nTotal time: {round(elapsed_time, 2)} seconds")
    print(f"Total cost: {round(total_cost, 5)}")

if __name__ == "__main__":
    main()
