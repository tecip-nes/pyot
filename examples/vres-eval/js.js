/*
 * Example Contiki test script (JavaScript).
 * A Contiki test script acts on mote output, such as via printf()'s.
 * The script may operate on the following variables:
 *  Mote mote, int id, String msg
 */

/* Make test automatically fail (timeout) after 100 simulated seconds */
//TIMEOUT(100000); /* milliseconds. no action at timeout */
importPackage(java.io);

TIMEOUT(70000000)
NUM_NODES = 5;
CONTROL_NODE = 7;
SENSOR_NODE = [3, 4, 5];
ACTUATOR_NODE = [9, 0xe, 0xa];
RUNS = 500;

var sensor_time = 0;//new Array();
var sensor_event_count = 0;//new Array();

function new_file(str) {
    return new FileWriter("firsttest.txt");
}

function mylog(str)
{
  log.log(str);
  file.write(str);
}

//returns true is the id is from a sensor node
function is_sensor_id()
{
  for (var i = 0; i <= SENSOR_NODE.length; i++) {
    if(id == SENSOR_NODE[i])
      return true;
  }
  return false;
}

function init_eval()
{
  sensor_time = 0;
  sensor_event_count = 0;

    /*for (var i = 0; i <= SENSOR_NODE.length; i++) {
    sensor_count[i] = 0;
  }*/

  actuator_count = 0;
  powerlog_count = 0;
  //num_samples = 0;
  sensor_id = -1;
  delay = -1;
  script_start_time = -1;
  script_end_time = -1;
  script_exec_time = -1
  miss = 0;
  sim_start_time = 0;

  file = new_file("");
  //powerlog_init();
  t = "\t";
  mylog("\nSeed: " + sim.getRandomSeed() + "\n");
  //print_topology();
  mylog(NUM_NODES + " nodes\n");
  //mylog(LOGIC_TYPE + " with logic in node " + PYCO_NODE + "\n");
  mylog("#\tSensor\tDelay\tPF time\n");
  mylog("\tID\t[us]\t[us]\n");

  GENERATE_MSG(4000, "wait");
  YIELD_THEN_WAIT_UNTIL(msg.equals("wait"));
}


function end_eval()
{
  //press_all_button();
  simtime = time - sim_start_time;
  mylog("missed= " + miss + t + "actuator messages" + t + actuator_count + " time " + simtime + "\n");
  file.close();
  //powerlog_stop();

  //if (PYCO_NODE == LAST_PYCO_NODE)
  log.testOK();

  //GENERATE_MSG(10000, "wait");
  //YIELD_THEN_WAIT_UNTIL(msg.equals("wait"));
  //press_all_button();
  //YIELD_THEN_WAIT_UNTIL(msg.indexOf("Application") != -1);
  //PYCO_NODE = id;
  //init_eval();
}


//plugin = mote.getSimulation().getGUI().getStartedPlugin("se.sics.cooja.plugins.analyzers");
//log.log("Starting script\n");
GENERATE_MSG(60000, "wait");
YIELD_THEN_WAIT_UNTIL(msg.equals("wait"));

  /* Select time in Radio Logger */
  /*plugin = mote.getSimulation().getCooja().getStartedPlugin("org.contikios.cooja.plugins.RadioLogger");
  if (plugin != null) {
    log.log("RadioLogger: Showing logged radio packet at mid simulation\n");
  }*/

init_eval();
log.log("Init done\n");
write(sim.getMoteWithID(7), "go");
sim_start_time = time;
//press_all_button();
YIELD_THEN_WAIT_UNTIL(msg.indexOf("Switching") != -1);
log.log("Starting control app\n");

while (true) {

  if (id==7 && msg.indexOf("T: ") != -1 /*&& sensor_id == -1*/) {
    //sensor_id = id;
    sensor_time = time;
    sensor_event_count++;
    delay = -1;
    //script_start_time = -1;
    //script_end_time = -1;
  }
  
  /*if (id == PYCO_NODE && msg.equals("(-") && script_start_time == -1) {
    script_start_time = time;
  }
  if (id == PYCO_NODE && msg.equals("-)") && script_end_time == -1 ) {
    script_end_time = time;
  }*/
    
  if (id == 7 && msg.indexOf("M: ") != -1) {
    miss ++;
  }


  if (id == ACTUATOR_NODE[0] && msg.indexOf("A: ") != -1 && delay == -1) {
    d0 = time - sensor_time;
    //sensor_time = 0;
    //actuator_count++;
    //script_exec_time = script_end_time - script_start_time;
    mylog((actuator_count) + t + d0 + t);
    //sensor_id = -1;
  }  

  if (id == ACTUATOR_NODE[1] && msg.indexOf("A: ") != -1 && delay == -1) {
    d1 = time - sensor_time;
    //sensor_time = 0;
    //actuator_count++;
    //script_exec_time = script_end_time - script_start_time;
    mylog(d1 + t);
    //sensor_id = -1;
  }  
    
        
  if (id == ACTUATOR_NODE[2] && msg.indexOf("A: ") != -1 && delay == -1) {
    delay = time - sensor_time;
    sensor_time = 0;
    actuator_count++;
    //script_exec_time = script_end_time - script_start_time;
    //data_size = plugin.getDataTraffic(sensor_time, time);    
    mylog(/*(actuator_count) + t + */ delay +/* t + data_size + */"\n");
    

    //sensor_id = -1;
  }

  if (actuator_count == RUNS){
    end_eval();
  }
  /*if (msg.indexOf("P: ") != -1) {
    powerlog_write();
  }

  if(powerlog_count == NUM_POWERLOG_ENTRY){
    end_eval();
  }*/

  YIELD();
}
